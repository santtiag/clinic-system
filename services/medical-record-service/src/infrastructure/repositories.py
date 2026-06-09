from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import (
    MedicalRecordORM, EvolutionNoteORM, PrescriptionORM, AttachmentORM,
)


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

    async def get_by_id(self, evolution_id: UUID) -> Optional[EvolutionNoteORM]:
        result = await self._session.execute(
            select(EvolutionNoteORM).where(EvolutionNoteORM.id == evolution_id)
        )
        return result.scalar_one_or_none()

    async def list_by_patient(self, patient_id: UUID) -> List[EvolutionNoteORM]:
        result = await self._session.execute(
            select(EvolutionNoteORM)
            .join(MedicalRecordORM, EvolutionNoteORM.record_id == MedicalRecordORM.id)
            .where(MedicalRecordORM.patient_id == patient_id)
            .order_by(EvolutionNoteORM.created_at.desc())
        )
        return result.scalars().all()


class PrescriptionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        record_id: UUID,
        doctor_id: UUID,
        medication: str,
        dosage: str,
        frequency: str,
        duration: str,
    ) -> PrescriptionORM:
        rx = PrescriptionORM(
            record_id=record_id,
            doctor_id=doctor_id,
            medication=medication,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
        )
        self._session.add(rx)
        await self._session.commit()
        await self._session.refresh(rx)
        return rx

    async def list_by_patient(self, patient_id: UUID) -> List[PrescriptionORM]:
        result = await self._session.execute(
            select(PrescriptionORM)
            .join(MedicalRecordORM, PrescriptionORM.record_id == MedicalRecordORM.id)
            .where(MedicalRecordORM.patient_id == patient_id)
            .order_by(PrescriptionORM.created_at.desc())
        )
        return result.scalars().all()


class AttachmentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        record_id: UUID,
        evolution_id: UUID,
        doctor_id: UUID,
        filename: str,
        content_type: str,
        file_path: str,
        file_size: int,
    ) -> AttachmentORM:
        attachment = AttachmentORM(
            record_id=record_id,
            evolution_id=evolution_id,
            doctor_id=doctor_id,
            filename=filename,
            content_type=content_type,
            file_path=file_path,
            file_size=file_size,
        )
        self._session.add(attachment)
        await self._session.commit()
        await self._session.refresh(attachment)
        return attachment

    async def list_by_evolution(self, evolution_id: UUID) -> List[AttachmentORM]:
        result = await self._session.execute(
            select(AttachmentORM)
            .where(AttachmentORM.evolution_id == evolution_id)
            .order_by(AttachmentORM.created_at.desc())
        )
        return result.scalars().all()
