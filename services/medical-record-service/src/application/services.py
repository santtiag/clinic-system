import os
import uuid
from pathlib import Path
from uuid import UUID
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories import (
    MedicalRecordRepository,
    EvolutionRepository,
    PrescriptionRepository,
    AttachmentRepository,
)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".dcm"}
ATTACHMENTS_DIR = Path(os.getenv("ATTACHMENTS_DIR", "/data/attachments"))


class MedicalRecordService:
    def __init__(self, session: AsyncSession):
        self._records = MedicalRecordRepository(session)
        self._evolutions = EvolutionRepository(session)
        self._prescriptions = PrescriptionRepository(session)
        self._attachments = AttachmentRepository(session)

    async def add_evolution(self, patient_id: UUID, doctor_id: UUID, observations: str):
        record = await self._records.get_or_create_by_patient(patient_id)
        note = await self._evolutions.create(record.id, doctor_id, observations)
        return note

    async def add_prescription(
        self,
        patient_id: UUID,
        doctor_id: UUID,
        medication: str,
        dosage: str,
        frequency: str,
        duration: str,
    ):
        record = await self._records.get_or_create_by_patient(patient_id)
        return await self._prescriptions.create(
            record.id, doctor_id, medication, dosage, frequency, duration
        )

    async def add_attachment(
        self,
        patient_id: UUID,
        doctor_id: UUID,
        evolution_id: UUID,
        file: UploadFile,
    ):
        record = await self._records.get_or_create_by_patient(patient_id)
        evolution = await self._evolutions.get_by_id(evolution_id)
        if not evolution or evolution.record_id != record.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Evolution not found for this patient")

        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Formato no permitido. Use PDF, JPEG, PNG o DICOM",
            )

        ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
        stored_name = f"{uuid.uuid4()}{ext}"
        dest = ATTACHMENTS_DIR / stored_name
        content = await file.read()
        dest.write_bytes(content)

        return await self._attachments.create(
            record_id=record.id,
            evolution_id=evolution_id,
            doctor_id=doctor_id,
            filename=file.filename or stored_name,
            content_type=file.content_type or "application/octet-stream",
            file_path=str(dest),
            file_size=len(content),
        )

    async def get_patient_history(self, patient_id: UUID):
        record = await self._records.get_or_create_by_patient(patient_id)
        evolutions = await self._evolutions.list_by_patient(patient_id)
        prescriptions = await self._prescriptions.list_by_patient(patient_id)
        attachments = []
        for evo in evolutions:
            attachments.extend(await self._attachments.list_by_evolution(evo.id))
        return {
            "record_id": record.id,
            "patient_id": patient_id,
            "evolutions": evolutions,
            "prescriptions": prescriptions,
            "attachments": attachments,
        }

    async def list_prescriptions(self, patient_id: UUID):
        return await self._prescriptions.list_by_patient(patient_id)
