from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import DoctorORM, AvailabilitySlotORM, AppointmentORM
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
    
    async def list_all(self) -> List[AppointmentORM]:
        result = await self._session.execute(
            select(AppointmentORM).order_by(AppointmentORM.created_at.desc())
        )
        return result.scalars().all()
