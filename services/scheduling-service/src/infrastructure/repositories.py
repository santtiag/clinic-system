from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import DoctorORM, AvailabilitySlotORM, AppointmentORM, AppointmentStatusHistoryORM
from src.domain.models import AppointmentStatus

class DoctorRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_by_specialty(self, specialty: str) -> List[DoctorORM]:
        result = await self._session.execute(
            select(DoctorORM).where(DoctorORM.specialty == specialty)
        )
        return result.scalars().all()

    async def get_by_id(self, doctor_id: UUID) -> Optional[DoctorORM]:
        result = await self._session.execute(
            select(DoctorORM).where(DoctorORM.id == doctor_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Optional[DoctorORM]:
        result = await self._session.execute(
            select(DoctorORM).where(DoctorORM.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[DoctorORM]:
        result = await self._session.execute(select(DoctorORM))
        return result.scalars().all()

    async def upsert(self, user_id: UUID, full_name: str, specialty: str) -> DoctorORM:
        doctor = await self.get_by_user_id(user_id)
        if doctor:
            doctor.full_name = full_name
            doctor.specialty = specialty
        else:
            doctor = DoctorORM(
                user_id=user_id, full_name=full_name, specialty=specialty
            )
            self._session.add(doctor)
        await self._session.commit()
        await self._session.refresh(doctor)
        return doctor


class AvailabilityRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_available(self, doctor_id: Optional[UUID] = None) -> List[AvailabilitySlotORM]:
        query = select(AvailabilitySlotORM).where(AvailabilitySlotORM.is_available == True)
        if doctor_id:
            query = query.where(AvailabilitySlotORM.doctor_id == doctor_id)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, slot_id: UUID) -> Optional[AvailabilitySlotORM]:
        result = await self._session.execute(
            select(AvailabilitySlotORM).where(AvailabilitySlotORM.id == slot_id)
        )
        return result.scalar_one_or_none()

    async def mark_booked(self, slot_id: UUID):
        slot = await self.get_by_id(slot_id)
        if slot:
            slot.is_available = False
            await self._session.commit()

    async def mark_available(self, slot_id: UUID):
        slot = await self.get_by_id(slot_id)
        if slot:
            slot.is_available = True
            await self._session.commit()


class AppointmentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, patient_id: UUID, doctor_id: UUID, slot_id: UUID,
                     reason: Optional[str]) -> AppointmentORM:
        appt = AppointmentORM(
            patient_id=patient_id,
            doctor_id=doctor_id,
            slot_id=slot_id,
            status=AppointmentStatus.SCHEDULED,
            reason=reason,
        )
        self._session.add(appt)
        await self._session.commit()
        await self._session.refresh(appt)
        return appt

    async def get_by_id(self, appointment_id: UUID) -> Optional[AppointmentORM]:
        result = await self._session.execute(
            select(AppointmentORM).where(AppointmentORM.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def list_by_patient(self, patient_id: UUID) -> List[AppointmentORM]:
        result = await self._session.execute(
            select(AppointmentORM)
            .where(AppointmentORM.patient_id == patient_id)
            .order_by(AppointmentORM.created_at.desc())
        )
        return result.scalars().all()
    
    async def list_by_doctor(self, doctor_id: UUID) -> List[AppointmentORM]:
        result = await self._session.execute(
            select(AppointmentORM)
            .where(AppointmentORM.doctor_id == doctor_id)
            .order_by(AppointmentORM.created_at.desc())
        )
        return result.scalars().all()

    async def list_all(self) -> List[AppointmentORM]:
        result = await self._session.execute(
            select(AppointmentORM).order_by(AppointmentORM.created_at.desc())
        )
        return result.scalars().all()


class AppointmentStatusHistoryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        appointment_id: UUID,
        old_status: str | None,
        new_status: str,
        changed_by: UUID | None,
        changed_by_role: str | None,
    ) -> AppointmentStatusHistoryORM:
        entry = AppointmentStatusHistoryORM(
            appointment_id=appointment_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            changed_by_role=changed_by_role,
        )
        self._session.add(entry)
        await self._session.commit()
        await self._session.refresh(entry)
        return entry

    async def list_by_appointment(self, appointment_id: UUID) -> List[AppointmentStatusHistoryORM]:
        result = await self._session.execute(
            select(AppointmentStatusHistoryORM)
            .where(AppointmentStatusHistoryORM.appointment_id == appointment_id)
            .order_by(AppointmentStatusHistoryORM.changed_at.asc())
        )
        return result.scalars().all()
