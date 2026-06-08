from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories import DoctorRepository, AvailabilityRepository, AppointmentRepository
from src.infrastructure.messaging import publish_event
from src.domain.models import AppointmentStatus

class SchedulingService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._doctors = DoctorRepository(session)
        self._slots = AvailabilityRepository(session)
        self._appointments = AppointmentRepository(session)

    async def search_availability(self, specialty: Optional[str] = None,
                                  doctor_id: Optional[UUID] = None):
        if specialty:
            docs = await self._doctors.list_by_specialty(specialty)
            doctor_ids = [d.id for d in docs]
            slots = []
            for did in doctor_ids:
                slots.extend(await self._slots.list_available(doctor_id=did))
            return slots
        return await self._slots.list_available(doctor_id=doctor_id)

    async def book_appointment(self, patient_id: UUID, slot_id: UUID,
                               reason: Optional[str]):
        slot = await self._slots.get_by_id(slot_id)
        if not slot or not slot.is_available:
            raise HTTPException(status.HTTP_409_CONFLICT, "Slot not available")
        await self._slots.mark_booked(slot_id)
        appt = await self._appointments.create(patient_id, slot.doctor_id, slot_id, reason)
        return appt

    async def list_patient_appointments(self, patient_id: UUID):
        appointments = await self._appointments.list_by_patient(patient_id)
        enriched = []
        for a in appointments:
            slot = await self._slots.get_by_id(a.slot_id)
            enriched.append({"appointment": a, "slot": slot})
        return enriched

    async def cancel_appointment(self, appointment_id: UUID, patient_id: UUID):
        appt = await self._appointments.get_by_id(appointment_id)
        if not appt or appt.patient_id != patient_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        if appt.status == AppointmentStatus.CANCELLED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Already cancelled")

        slot = await self._slots.get_by_id(appt.slot_id)
        if not slot:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Associated slot not found")

        now = datetime.now()
        if now > (slot.start_time - timedelta(hours=24)):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Cannot cancel within 24 hours before appointment"
            )

        appt.status = AppointmentStatus.CANCELLED
        await self._session.commit()
        await self._slots.mark_available(appt.slot_id)

        await publish_event("appointments.cancelled", {
            "appointment_id": str(appt.id),
            "patient_id": str(patient_id),
            "slot_id": str(appt.slot_id),
            "cancelled_at": now.isoformat(),
        })
        return appt

    async def reschedule_appointment(self, appointment_id: UUID, patient_id: UUID,
                                     new_slot_id: UUID):
        appt = await self._appointments.get_by_id(appointment_id)
        if not appt or appt.patient_id != patient_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        if appt.status == AppointmentStatus.CANCELLED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Cannot reschedule a cancelled appointment")

        new_slot = await self._slots.get_by_id(new_slot_id)
        if not new_slot or not new_slot.is_available:
            raise HTTPException(status.HTTP_409_CONFLICT, "New slot not available")

        old_slot_id = appt.slot_id

        await self._slots.mark_booked(new_slot_id)
        await self._slots.mark_available(old_slot_id)

        appt.slot_id = new_slot_id
        appt.status = AppointmentStatus.SCHEDULED
        await self._session.commit()

        await publish_event("appointments.rescheduled", {
            "appointment_id": str(appt.id),
            "patient_id": str(patient_id),
            "old_slot_id": str(old_slot_id),
            "new_slot_id": str(new_slot_id),
            "rescheduled_at": datetime.utcnow().isoformat(),
        })
        return appt
    
    async def update_appointment_status(self, appointment_id: UUID, new_status: str, user_role: str):
        if user_role not in ("doctor", "admin", "staff"):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only medical staff can update status")

        appt = await self._appointments.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")

        current = appt.status
        target = AppointmentStatus(new_status)

        allowed = {
            AppointmentStatus.SCHEDULED: [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED],
            AppointmentStatus.CONFIRMED: [AppointmentStatus.IN_ATTENTION, AppointmentStatus.CANCELLED],
            AppointmentStatus.IN_ATTENTION: [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED],
        }
        if target not in allowed.get(current, []):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Invalid transition from {current.value} to {target.value}"
            )

        appt.status = target
        await self._session.commit()

        await publish_event("appointments.status_updated", {
            "appointment_id": str(appt.id),
            "patient_id": str(appt.patient_id),
            "doctor_id": str(appt.doctor_id),
            "old_status": current.value,
            "new_status": target.value,
            "updated_at": datetime.now().isoformat(),
        })

        return appt
    
    async def list_all_appointments(self):
        return await self._appointments.list_all()
