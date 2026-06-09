from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import SessionLocal
from src.presentation.schemas import (
    EvolutionCreate, EvolutionResponse, MedicalRecordResponse,
    PrescriptionCreate, PrescriptionResponse, AttachmentResponse,
)
from src.application.services import MedicalRecordService
from src.presentation.dependencies import get_current_user, require_doctor, require_clinical_access

router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session


def _build_record_response(data: dict) -> MedicalRecordResponse:
    return MedicalRecordResponse(
        record_id=data["record_id"],
        patient_id=data["patient_id"],
        evolutions=[
            EvolutionResponse(
                id=e.id, record_id=e.record_id, doctor_id=e.doctor_id,
                observations=e.observations, created_at=e.created_at,
            ) for e in data["evolutions"]
        ],
        prescriptions=[
            PrescriptionResponse(
                id=p.id, record_id=p.record_id, doctor_id=p.doctor_id,
                medication=p.medication, dosage=p.dosage,
                frequency=p.frequency, duration=p.duration, created_at=p.created_at,
            ) for p in data["prescriptions"]
        ],
        attachments=[
            AttachmentResponse(
                id=a.id, record_id=a.record_id, evolution_id=a.evolution_id,
                doctor_id=a.doctor_id, filename=a.filename,
                content_type=a.content_type, file_size=a.file_size, created_at=a.created_at,
            ) for a in data["attachments"]
        ],
    )


def _check_patient_access(current_user: dict, patient_id: UUID):
    if current_user.get("role") == "patient" and str(patient_id) != current_user.get("user_id"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot access another patient's records")


@router.get("/records/me", response_model=MedicalRecordResponse)
async def my_record(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "patient":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only patients can use /records/me")
    service = MedicalRecordService(db)
    data = await service.get_patient_history(UUID(current_user["user_id"]))
    return _build_record_response(data)


@router.post("/records/{patient_id}/evolutions", status_code=status.HTTP_201_CREATED, response_model=EvolutionResponse)
async def add_evolution(
    patient_id: UUID,
    payload: EvolutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_doctor),
):
    service = MedicalRecordService(db)
    note = await service.add_evolution(
        patient_id=patient_id,
        doctor_id=UUID(current_user["user_id"]),
        observations=payload.observations,
    )
    return EvolutionResponse(
        id=note.id, record_id=note.record_id, doctor_id=note.doctor_id,
        observations=note.observations, created_at=note.created_at,
    )


@router.post("/records/{patient_id}/prescriptions", status_code=status.HTTP_201_CREATED, response_model=PrescriptionResponse)
async def add_prescription(
    patient_id: UUID,
    payload: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_doctor),
):
    service = MedicalRecordService(db)
    rx = await service.add_prescription(
        patient_id=patient_id,
        doctor_id=UUID(current_user["user_id"]),
        medication=payload.medication,
        dosage=payload.dosage,
        frequency=payload.frequency,
        duration=payload.duration,
    )
    return PrescriptionResponse(
        id=rx.id, record_id=rx.record_id, doctor_id=rx.doctor_id,
        medication=rx.medication, dosage=rx.dosage,
        frequency=rx.frequency, duration=rx.duration, created_at=rx.created_at,
    )


@router.get("/records/{patient_id}/prescriptions", response_model=List[PrescriptionResponse])
async def list_prescriptions(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_clinical_access),
):
    _check_patient_access(current_user, patient_id)
    service = MedicalRecordService(db)
    prescriptions = await service.list_prescriptions(patient_id)
    return [
        PrescriptionResponse(
            id=p.id, record_id=p.record_id, doctor_id=p.doctor_id,
            medication=p.medication, dosage=p.dosage,
            frequency=p.frequency, duration=p.duration, created_at=p.created_at,
        ) for p in prescriptions
    ]


@router.post("/records/{patient_id}/attachments", status_code=status.HTTP_201_CREATED, response_model=AttachmentResponse)
async def add_attachment(
    patient_id: UUID,
    evolution_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_doctor),
):
    service = MedicalRecordService(db)
    attachment = await service.add_attachment(
        patient_id=patient_id,
        doctor_id=UUID(current_user["user_id"]),
        evolution_id=evolution_id,
        file=file,
    )
    return AttachmentResponse(
        id=attachment.id, record_id=attachment.record_id,
        evolution_id=attachment.evolution_id, doctor_id=attachment.doctor_id,
        filename=attachment.filename, content_type=attachment.content_type,
        file_size=attachment.file_size, created_at=attachment.created_at,
    )


@router.get("/records/{patient_id}", response_model=MedicalRecordResponse)
async def get_history(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_clinical_access),
):
    _check_patient_access(current_user, patient_id)
    service = MedicalRecordService(db)
    data = await service.get_patient_history(patient_id)
    return _build_record_response(data)
