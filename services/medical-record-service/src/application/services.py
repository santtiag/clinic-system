from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories import MedicalRecordRepository, EvolutionRepository

class MedicalRecordService:
    def __init__(self, session: AsyncSession):
        self._records = MedicalRecordRepository(session)
        self._evolutions = EvolutionRepository(session)

    async def add_evolution(self, patient_id: UUID, doctor_id: UUID, observations: str):
        record = await self._records.get_or_create_by_patient(patient_id)
        note = await self._evolutions.create(record.id, doctor_id, observations)
        return note

    async def get_patient_history(self, patient_id: UUID):
        record = await self._records.get_or_create_by_patient(patient_id)
        evolutions = await self._evolutions.list_by_patient(patient_id)
        return {
            "record_id": record.id,
            "patient_id": patient_id,
            "evolutions": evolutions,
        }
