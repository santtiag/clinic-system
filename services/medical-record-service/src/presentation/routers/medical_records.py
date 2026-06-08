"""
Medical Record routers.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer

from common.database import get_db
from common.security import decode_token
from common.exceptions import UnauthorizedException, NotFoundException

from src.domain.services import (
    MedicalRecordService, ClinicalNoteService,
    PrescriptionService, DiagnosisService, MedicalDocumentService
)
from src.domain.entities import ClinicalNoteType
from src.presentation.schemas import (
    MedicalRecordCreate, MedicalRecordResponse, MedicalRecordDetailResponse,
    ClinicalNoteCreate, ClinicalNoteResponse, ClinicalNoteDetailResponse,
    ClinicalNoteListResponse, PrescriptionCreate, PrescriptionResponse,
    PrescriptionListResponse, DiagnosisCreate, DiagnosisResponse,
    MedicalDocumentCreate, MedicalDocumentResponse,
    FrequentDiagnosisResponse, TimelineEntry
)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise UnauthorizedException("Missing authentication")
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")
    return payload


def _to_medical_record_response(record) -> MedicalRecordResponse:
    return MedicalRecordResponse(
        id=record.id,
        patientId=record.patient_id,
        recordNumber=record.record_number,
        isActive=record.is_active,
        createdAt=record.created_at,
        updatedAt=record.updated_at
    )


def _to_clinical_note_response(note) -> ClinicalNoteResponse:
    return ClinicalNoteResponse(
        id=note.id,
        medicalRecordId=note.medical_record_id,
        doctorId=note.doctor_id,
        appointmentId=note.appointment_id,
        noteType=note.note_type.value,
        chiefComplaint=note.chief_complaint,
        presentIllness=note.present_illness,
        physicalExam=note.physical_exam,
        evolution=note.evolution,
        observations=note.observations,
        createdAt=note.created_at,
        updatedAt=note.updated_at
    )


def _to_prescription_response(p) -> PrescriptionResponse:
    return PrescriptionResponse(
        id=p.id,
        clinicalNoteId=p.clinical_note_id,
        medicationName=p.medication_name,
        dosage=p.dosage,
        frequency=p.frequency,
        duration=p.duration,
        route=p.route,
        instructions=p.instructions,
        createdAt=p.created_at
    )


def _to_diagnosis_response(d) -> DiagnosisResponse:
    return DiagnosisResponse(
        id=d.id,
        clinicalNoteId=d.clinical_note_id,
        cie10Code=d.cie10_code,
        description=d.description,
        diagnosisType=d.diagnosis_type,
        createdAt=d.created_at
    )


def _to_document_response(doc) -> MedicalDocumentResponse:
    return MedicalDocumentResponse(
        id=doc.id,
        clinicalNoteId=doc.clinical_note_id,
        fileName=doc.file_name,
        fileType=doc.file_type,
        filePath=doc.file_path,
        fileSize=doc.file_size,
        description=doc.description,
        uploadedBy=doc.uploaded_by,
        createdAt=doc.created_at
    )


# ====================
# MEDICAL RECORDS
# ====================

@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    request: MedicalRecordCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new medical record for a patient."""
    service = MedicalRecordService(db)
    record = await service.create_medical_record(UUID(request.patient_id))
    return _to_medical_record_response(record)


@router.get("/{record_id}", response_model=MedicalRecordDetailResponse)
async def get_medical_record(
    record_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get medical record with all clinical notes."""
    service = MedicalRecordService(db)
    record = await service.get_medical_record(record_id)
    if not record:
        raise NotFoundException("MedicalRecord", record_id)

    return MedicalRecordDetailResponse(
        id=record.id,
        patientId=record.patient_id,
        recordNumber=record.record_number,
        isActive=record.is_active,
        createdAt=record.created_at,
        updatedAt=record.updated_at,
        clinicalNotes=[
            ClinicalNoteDetailResponse(
                id=note.id,
                medicalRecordId=note.medical_record_id,
                doctorId=note.doctor_id,
                appointmentId=note.appointment_id,
                noteType=note.note_type.value,
                chiefComplaint=note.chief_complaint,
                presentIllness=note.present_illness,
                physicalExam=note.physical_exam,
                evolution=note.evolution,
                observations=note.observations,
                createdAt=note.created_at,
                updatedAt=note.updated_at,
                diagnoses=[_to_diagnosis_response(d) for d in note.diagnoses],
                prescriptions=[_to_prescription_response(p) for p in note.prescriptions],
                documents=[_to_document_response(doc) for doc in note.documents]
            )
            for note in record.clinical_notes
        ]
    )


@router.get("/patient/{patient_id}", response_model=MedicalRecordDetailResponse)
async def get_medical_record_by_patient(
    patient_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get medical record by patient ID."""
    service = MedicalRecordService(db)
    record = await service.get_medical_record_by_patient(patient_id)
    if not record:
        raise NotFoundException("MedicalRecord", patient_id)

    return MedicalRecordDetailResponse(
        id=record.id,
        patientId=record.patient_id,
        recordNumber=record.record_number,
        isActive=record.is_active,
        createdAt=record.created_at,
        updatedAt=record.updated_at,
        clinicalNotes=[
            ClinicalNoteDetailResponse(
                id=note.id,
                medicalRecordId=note.medical_record_id,
                doctorId=note.doctor_id,
                appointmentId=note.appointment_id,
                noteType=note.note_type.value,
                chiefComplaint=note.chief_complaint,
                presentIllness=note.present_illness,
                physicalExam=note.physical_exam,
                evolution=note.evolution,
                observations=note.observations,
                createdAt=note.created_at,
                updatedAt=note.updated_at,
                diagnoses=[_to_diagnosis_response(d) for d in note.diagnoses],
                prescriptions=[_to_prescription_response(p) for p in note.prescriptions],
                documents=[_to_document_response(doc) for doc in note.documents]
            )
            for note in record.clinical_notes
        ]
    )


# ====================
# CLINICAL NOTES
# ====================

@router.post("/clinical-notes", response_model=ClinicalNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_clinical_note(
    request: ClinicalNoteCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new clinical note."""
    service = ClinicalNoteService(db)
    note = await service.create_clinical_note(
        medical_record_id=UUID(request.medical_record_id),
        doctor_id=UUID(request.doctor_id),
        note_type=ClinicalNoteType(request.note_type),
        chief_complaint=request.chief_complaint,
        present_illness=request.present_illness,
        physical_exam=request.physical_exam,
        evolution=request.evolution,
        observations=request.observations,
        appointment_id=UUID(request.appointment_id) if request.appointment_id else None
    )
    return _to_clinical_note_response(note)


@router.get("/clinical-notes/{note_id}", response_model=ClinicalNoteDetailResponse)
async def get_clinical_note(
    note_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get clinical note with diagnoses, prescriptions and documents."""
    service = ClinicalNoteService(db)
    note = await service.get_clinical_note(note_id)
    if not note:
        raise NotFoundException("ClinicalNote", note_id)

    return ClinicalNoteDetailResponse(
        id=note.id,
        medicalRecordId=note.medical_record_id,
        doctorId=note.doctor_id,
        appointmentId=note.appointment_id,
        noteType=note.note_type.value,
        chiefComplaint=note.chief_complaint,
        presentIllness=note.present_illness,
        physicalExam=note.physical_exam,
        evolution=note.evolution,
        observations=note.observations,
        createdAt=note.created_at,
        updatedAt=note.updated_at,
        diagnoses=[_to_diagnosis_response(d) for d in note.diagnoses],
        prescriptions=[_to_prescription_response(p) for p in note.prescriptions],
        documents=[_to_document_response(doc) for doc in note.documents]
    )


@router.get("/clinical-notes/medical-record/{medical_record_id}", response_model=ClinicalNoteListResponse)
async def get_clinical_notes_by_medical_record(
    medical_record_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get clinical notes for a medical record with pagination."""
    service = ClinicalNoteService(db)
    notes, total = await service.get_notes_by_medical_record(medical_record_id, page, page_size)

    return ClinicalNoteListResponse(
        items=[_to_clinical_note_response(n) for n in notes],
        total=total,
        page=page,
        pageSize=page_size
    )


# ====================
# PRESCRIPTIONS
# ====================

@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    request: PrescriptionCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new prescription."""
    service = PrescriptionService(db)
    prescription = await service.create_prescription(
        clinical_note_id=UUID(request.clinical_note_id),
        medication_name=request.medication_name,
        dosage=request.dosage,
        frequency=request.frequency,
        duration=request.duration,
        route=request.route,
        instructions=request.instructions
    )
    return _to_prescription_response(prescription)


@router.get("/prescriptions/clinical-note/{clinical_note_id}", response_model=List[PrescriptionResponse])
async def get_prescriptions_by_clinical_note(
    clinical_note_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get prescriptions for a clinical note."""
    service = PrescriptionService(db)
    prescriptions = await service.get_prescriptions_by_clinical_note(clinical_note_id)
    return [_to_prescription_response(p) for p in prescriptions]


@router.get("/prescriptions/patient/{medical_record_id}", response_model=PrescriptionListResponse)
async def get_patient_prescriptions(
    medical_record_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get all prescriptions for a patient."""
    service = PrescriptionService(db)
    prescriptions, total = await service.get_patient_prescriptions(medical_record_id, page, page_size)

    return PrescriptionListResponse(
        items=[_to_prescription_response(p) for p in prescriptions],
        total=total,
        page=page,
        pageSize=page_size
    )


# ====================
# DIAGNOSES
# ====================

@router.post("/diagnoses", response_model=DiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(
    request: DiagnosisCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new diagnosis."""
    service = DiagnosisService(db)
    diagnosis = await service.create_diagnosis(
        clinical_note_id=UUID(request.clinical_note_id),
        cie10_code=request.cie10_code,
        description=request.description,
        diagnosis_type=request.diagnosis_type
    )
    return _to_diagnosis_response(diagnosis)


@router.get("/diagnoses/clinical-note/{clinical_note_id}", response_model=List[DiagnosisResponse])
async def get_diagnoses_by_clinical_note(
    clinical_note_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get diagnoses for a clinical note."""
    service = DiagnosisService(db)
    diagnoses = await service.get_diagnoses_by_clinical_note(clinical_note_id)
    return [_to_diagnosis_response(d) for d in diagnoses]


@router.get("/diagnoses/frequent", response_model=List[FrequentDiagnosisResponse])
async def get_frequent_diagnoses(
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get most frequent CIE-10 diagnoses."""
    service = DiagnosisService(db)
    results = await service.get_most_frequent_diagnoses(limit=limit)
    return [FrequentDiagnosisResponse(cie10Code=code, count=count) for code, count in results]


# ====================
# DOCUMENTS
# ====================

@router.post("/documents", response_model=MedicalDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: MedicalDocumentCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a document record."""
    service = MedicalDocumentService(db)
    document = await service.create_document(
        clinical_note_id=UUID(request.clinical_note_id),
        file_name=request.file_name,
        file_type=request.file_type,
        file_path=request.file_path,
        file_size=request.file_size,
        description=request.description,
        uploaded_by=UUID(current_user.user_id)
    )
    return _to_document_response(document)


@router.get("/documents/clinical-note/{clinical_note_id}", response_model=List[MedicalDocumentResponse])
async def get_documents_by_clinical_note(
    clinical_note_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get documents for a clinical note."""
    service = MedicalDocumentService(db)
    documents = await service.get_documents_by_clinical_note(clinical_note_id)
    return [_to_document_response(doc) for doc in documents]


# ====================
# TIMELINE
# ====================

@router.get("/timeline/{medical_record_id}", response_model=List[TimelineEntry])
async def get_timeline(
    medical_record_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get chronological timeline of a patient's medical history."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from src.domain.entities import ClinicalNote

    result = await db.execute(
        select(ClinicalNote)
        .options(
            selectinload(ClinicalNote.diagnoses),
            selectinload(ClinicalNote.prescriptions)
        )
        .where(ClinicalNote.medical_record_id == medical_record_id)
        .order_by(ClinicalNote.created_at.desc())
    )
    notes = result.scalars().all()

    timeline = []
    for note in notes:
        timeline.append(TimelineEntry(
            date=note.created_at,
            type="consultation",
            title=f"Consulta - {note.note_type.value}",
            description=note.chief_complaint or note.observations,
            doctorId=note.doctor_id
        ))
        for diag in note.diagnoses:
            timeline.append(TimelineEntry(
                date=diag.created_at,
                type="diagnosis",
                title=f"Diagnóstico: {diag.cie10_code}",
                description=diag.description,
                doctorId=note.doctor_id
            ))
        for presc in note.prescriptions:
            timeline.append(TimelineEntry(
                date=presc.created_at,
                type="prescription",
                title=f"Prescripción: {presc.medication_name}",
                description=f"{presc.dosage} - {presc.frequency} - {presc.duration}",
                doctorId=note.doctor_id
            ))

    timeline.sort(key=lambda x: x.date, reverse=True)
    return timeline
