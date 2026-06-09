from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories import (
    DoctorRepository,
    AvailabilityRepository,
    AppointmentRepository,
    AppointmentStatusHistoryRepository,
)
from src.infrastructure.messaging import publish_event
from src.domain.models import AppointmentStatus

ROLE_TRANSITIONS = {
    "staff": {
        AppointmentStatus.SCHEDULED: [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED],
        AppointmentStatus.CONFIRMED: [AppointmentStatus.CANCELLED],
    },
    "admin": {
        AppointmentStatus.SCHEDULED: [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED],
        AppointmentStatus.CONFIRMED: [AppointmentStatus.CANCELLED, AppointmentStatus.IN_ATTENTION],
        AppointmentStatus.IN_ATTENTION: [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED],
    },
    "doctor": {
        AppointmentStatus.CONFIRMED: [AppointmentStatus.IN_ATTENTION, AppointmentStatus.CANCELLED],
        AppointmentStatus.IN_ATTENTION: [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED],
    },
}


class SchedulingService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._doctors = DoctorRepository(session)
        self._slots = AvailabilityRepository(session)
        self._appointments = AppointmentRepository(session)
        self._history = AppointmentStatusHistoryRepository(session)

    async def _doctor_map(self) -> dict:
        doctors = await self._doctors.list_all()
        return {d.id: d for d in doctors}

    async def list_doctors(self, specialty: Optional[str] = None):
        if specialty:
            return await self._doctors.list_by_specialty(specialty)
        return await self._doctors.list_all()

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
        await publish_event("appointments.created", {
            "appointment_id": str(appt.id),
            "patient_id": str(patient_id),
            "doctor_id": str(appt.doctor_id),
        })
        return appt

    async def list_patient_appointments(self, patient_id: UUID):
        appointments = await self._appointments.list_by_patient(patient_id)
        doctors = await self._doctor_map()
        enriched = []
        for a in appointments:
            slot = await self._slots.get_by_id(a.slot_id)
            enriched.append(
                {"appointment": a, "slot": slot, "doctor": doctors.get(a.doctor_id)}
            )
        return enriched

    async def list_doctor_appointments(self, user_id: UUID):
        doctor = await self._doctors.get_by_user_id(user_id)
        if not doctor:
            return []
        appointments = await self._appointments.list_by_doctor(doctor.id)
        enriched = []
        for a in appointments:
            slot = await self._slots.get_by_id(a.slot_id)
            enriched.append({"appointment": a, "slot": slot, "doctor": doctor})
        return enriched

    async def list_all_appointments_enriched(self):
        appointments = await self._appointments.list_all()
        doctors = await self._doctor_map()
        enriched = []
        for a in appointments:
            slot = await self._slots.get_by_id(a.slot_id)
            enriched.append(
                {"appointment": a, "slot": slot, "doctor": doctors.get(a.doctor_id)}
            )
        return enriched

    async def assign_doctor(self, appointment_id: UUID, doctor_id: UUID,
                            user_id: UUID | None, user_role: str):
        appt = await self._appointments.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        if appt.status == AppointmentStatus.CANCELLED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Cannot assign a cancelled appointment")
        new_doctor = await self._doctors.get_by_id(doctor_id)
        if not new_doctor:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found")
        current_slot = await self._slots.get_by_id(appt.slot_id)
        current_doctor = await self._doctors.get_by_id(appt.doctor_id)
        if current_doctor and current_doctor.specialty != new_doctor.specialty:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Assigned doctor specialty does not match the appointment specialty",
            )
        appt.doctor_id = new_doctor.id
        await self._session.commit()
        await self._history.create(
            appt.id, appt.status.value, appt.status.value, user_id, user_role
        )
        await publish_event("appointments.assigned", {
            "appointment_id": str(appt.id),
            "doctor_id": str(new_doctor.id),
            "assigned_by": str(user_id) if user_id else None,
        })
        return appt

    async def cancel_appointment(
        self,
        appointment_id: UUID,
        patient_id: UUID | None,
        user_role: str,
        enforce_window: bool = True,
    ):
        appt = await self._appointments.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        if user_role == "patient" and appt.patient_id != patient_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        if appt.status == AppointmentStatus.CANCELLED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Already cancelled")

        slot = await self._slots.get_by_id(appt.slot_id)
        if not slot:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Associated slot not found")

        if enforce_window and user_role == "patient":
            now = datetime.now()
            if now > (slot.start_time - timedelta(hours=24)):
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "Cannot cancel within 24 hours before appointment",
                )

        old_status = appt.status.value
        appt.status = AppointmentStatus.CANCELLED
        await self._session.commit()
        await self._slots.mark_available(appt.slot_id)
        await self._history.create(
            appt.id, old_status, AppointmentStatus.CANCELLED.value, patient_id, user_role
        )

        await publish_event("appointments.cancelled", {
            "appointment_id": str(appt.id),
            "patient_id": str(appt.patient_id),
            "slot_id": str(appt.slot_id),
            "cancelled_at": datetime.now().isoformat(),
        })
        return appt

    async def reschedule_appointment(self, appointment_id: UUID, new_slot_id: UUID,
                                     user_id: UUID | None, user_role: str):
        appt = await self._appointments.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        if appt.status == AppointmentStatus.CANCELLED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Cannot reschedule a cancelled appointment")

        new_slot = await self._slots.get_by_id(new_slot_id)
        if not new_slot or not new_slot.is_available:
            raise HTTPException(status.HTTP_409_CONFLICT, "New slot not available")

        # El nuevo horario debe pertenecer a un médico de la misma especialidad.
        current_doctor = await self._doctors.get_by_id(appt.doctor_id)
        new_doctor = await self._doctors.get_by_id(new_slot.doctor_id)
        if current_doctor and new_doctor and current_doctor.specialty != new_doctor.specialty:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "New slot belongs to a doctor of a different specialty",
            )

        old_slot_id = appt.slot_id
        await self._slots.mark_booked(new_slot_id)
        await self._slots.mark_available(old_slot_id)

        old_status = appt.status.value
        appt.slot_id = new_slot_id
        appt.doctor_id = new_slot.doctor_id
        appt.status = AppointmentStatus.SCHEDULED
        await self._session.commit()
        await self._history.create(
            appt.id, old_status, AppointmentStatus.SCHEDULED.value, user_id, user_role
        )

        await publish_event("appointments.rescheduled", {
            "appointment_id": str(appt.id),
            "patient_id": str(appt.patient_id),
            "old_slot_id": str(old_slot_id),
            "new_slot_id": str(new_slot_id),
            "rescheduled_at": datetime.now().isoformat(),
        })
        return appt

    async def update_appointment_status(
        self,
        appointment_id: UUID,
        new_status: str,
        user_role: str,
        user_id: UUID | None = None,
    ):
        if user_role not in ROLE_TRANSITIONS and user_role != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only medical staff can update status")

        appt = await self._appointments.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")

        current = appt.status
        target = AppointmentStatus(new_status)
        allowed_map = ROLE_TRANSITIONS.get(user_role, ROLE_TRANSITIONS["admin"])
        if target not in allowed_map.get(current, []):
            valid = [s.value for s in allowed_map.get(current, [])]
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Invalid transition from {current.value} to {target.value}. Valid: {valid}",
            )

        old_status = current.value
        appt.status = target
        await self._session.commit()
        await self._history.create(appt.id, old_status, target.value, user_id, user_role)

        await publish_event("appointments.status_updated", {
            "appointment_id": str(appt.id),
            "patient_id": str(appt.patient_id),
            "doctor_id": str(appt.doctor_id),
            "old_status": old_status,
            "new_status": target.value,
            "updated_at": datetime.now().isoformat(),
        })

        return appt

    async def list_all_appointments(self):
        return await self._appointments.list_all()

    async def get_status_history(self, appointment_id: UUID):
        appt = await self._appointments.get_by_id(appointment_id)
        if not appt:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
        return await self._history.list_by_appointment(appointment_id)
