from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import MedicalRecordORM, EvolutionNoteORM

class MedicalRecordRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_or_create_by_patient(self, patient_id: UUID) -> MedicalRecordORM:
        result = await self._session.execute(
            select(MedicalRecordORM).where(MedicalRecordORM.patient_id == patient_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            record = MedicalRecordORM(patient_id=patient_id)
            self._session.add(record)
            await self._session.commit()
            await self._session.refresh(record)
        return record

class EvolutionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, record_id: UUID, doctor_id: UUID, observations: str) -> EvolutionNoteORM:
        note = EvolutionNoteORM(
            record_id=record_id,
            doctor_id=doctor_id,
            observations=observations,
        )
        self._session.add(note)
        await self._session.commit()
        await self._session.refresh(note)
        return note

    async def list_by_patient(self, patient_id: UUID) -> List[EvolutionNoteORM]:
        result = await self._session.execute(
            select(EvolutionNoteORM)
            .join(MedicalRecordORM, EvolutionNoteORM.record_id == MedicalRecordORM.id)
            .where(MedicalRecordORM.patient_id == patient_id)
            .order_by(EvolutionNoteORM.created_at.desc())
        )
        return result.scalars().all()
