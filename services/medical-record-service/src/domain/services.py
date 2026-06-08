"""
Domain services for Medical Record Service.
"""

from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from common.exceptions import NotFoundException, ValidationException, ForbiddenException
from common.logging import get_logger

from src.domain.entities import (
    MedicalRecord, ClinicalNote, Diagnosis,
    Prescription, MedicalDocument, ClinicalNoteType
)


logger = get_logger(__name__)


class MedicalRecordService:
    """Service for managing medical records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_medical_record(self, patient_id: UUID) -> MedicalRecord:
        """Create a new medical record for a patient."""
        # Generate record number: MR-YYYYMMDD-XXXX
        record_number = f"MR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(patient_id)[:4].upper()}"

        record = MedicalRecord(
            patient_id=patient_id,
            record_number=record_number,
            is_active=True
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)

        logger.info(f"Medical record created: {record.id} for patient {patient_id}")
        return record

    async def get_medical_record(self, record_id: UUID) -> Optional[MedicalRecord]:
        """Get medical record by ID with all related data."""
        from sqlalchemy.orm import selectinload
        result = await self.db.execute(
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.clinical_notes)
                .selectinload(ClinicalNote.diagnoses),
                selectinload(MedicalRecord.clinical_notes)
                .selectinload(ClinicalNote.prescriptions),
                selectinload(MedicalRecord.clinical_notes)
                .selectinload(ClinicalNote.documents)
            )
            .where(MedicalRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_medical_record_by_patient(self, patient_id: UUID) -> Optional[MedicalRecord]:
        """Get medical record by patient ID."""
        from sqlalchemy.orm import selectinload
        result = await self.db.execute(
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.clinical_notes)
                .selectinload(ClinicalNote.diagnoses),
                selectinload(MedicalRecord.clinical_notes)
                .selectinload(ClinicalNote.prescriptions),
                selectinload(MedicalRecord.clinical_notes)
                .selectinload(ClinicalNote.documents)
            )
            .where(MedicalRecord.patient_id == patient_id)
        )
        return result.scalar_one_or_none()


class ClinicalNoteService:
    """Service for managing clinical notes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_clinical_note(
        self,
        medical_record_id: UUID,
        doctor_id: UUID,
        note_type: ClinicalNoteType,
        chief_complaint: Optional[str] = None,
        present_illness: Optional[str] = None,
        physical_exam: Optional[str] = None,
        evolution: Optional[str] = None,
        observations: Optional[str] = None,
        appointment_id: Optional[UUID] = None
    ) -> ClinicalNote:
        """Create a new clinical note."""
        # Verify medical record exists
        result = await self.db.execute(
            select(MedicalRecord).where(MedicalRecord.id == medical_record_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundException("MedicalRecord", medical_record_id)

        note = ClinicalNote(
            medical_record_id=medical_record_id,
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            note_type=note_type,
            chief_complaint=chief_complaint,
            present_illness=present_illness,
            physical_exam=physical_exam,
            evolution=evolution,
            observations=observations
        )
        self.db.add(note)
        await self.db.flush()
        await self.db.refresh(note)

        logger.info(f"Clinical note created: {note.id}")
        return note

    async def get_clinical_note(self, note_id: UUID) -> Optional[ClinicalNote]:
        """Get clinical note by ID with all related data."""
        from sqlalchemy.orm import selectinload
        result = await self.db.execute(
            select(ClinicalNote)
            .options(
                selectinload(ClinicalNote.diagnoses),
                selectinload(ClinicalNote.prescriptions),
                selectinload(ClinicalNote.documents)
            )
            .where(ClinicalNote.id == note_id)
        )
        return result.scalar_one_or_none()

    async def get_notes_by_medical_record(
        self,
        medical_record_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ClinicalNote], int]:
        """Get clinical notes for a medical record with pagination."""
        offset = (page - 1) * page_size

        count_result = await self.db.execute(
            select(func.count(ClinicalNote.id))
            .where(ClinicalNote.medical_record_id == medical_record_id)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(ClinicalNote)
            .where(ClinicalNote.medical_record_id == medical_record_id)
            .order_by(ClinicalNote.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        notes = list(result.scalars().all())

        return notes, total


class PrescriptionService:
    """Service for managing prescriptions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_prescription(
        self,
        clinical_note_id: UUID,
        medication_name: str,
        dosage: str,
        frequency: str,
        duration: str,
        route: Optional[str] = None,
        instructions: Optional[str] = None
    ) -> Prescription:
        """Create a new prescription."""
        prescription = Prescription(
            clinical_note_id=clinical_note_id,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            route=route,
            instructions=instructions
        )
        self.db.add(prescription)
        await self.db.flush()
        await self.db.refresh(prescription)

        logger.info(f"Prescription created: {prescription.id}")
        return prescription

    async def get_prescriptions_by_clinical_note(
        self, clinical_note_id: UUID
    ) -> List[Prescription]:
        """Get prescriptions for a clinical note."""
        result = await self.db.execute(
            select(Prescription)
            .where(Prescription.clinical_note_id == clinical_note_id)
            .order_by(Prescription.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_patient_prescriptions(
        self,
        medical_record_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Prescription], int]:
        """Get all prescriptions for a patient through their medical record."""
        from sqlalchemy.orm import joinedload
        offset = (page - 1) * page_size

        count_result = await self.db.execute(
            select(func.count(Prescription.id))
            .join(ClinicalNote)
            .where(ClinicalNote.medical_record_id == medical_record_id)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(Prescription)
            .join(ClinicalNote)
            .where(ClinicalNote.medical_record_id == medical_record_id)
            .order_by(Prescription.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        prescriptions = list(result.scalars().all())

        return prescriptions, total


class DiagnosisService:
    """Service for managing diagnoses."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_diagnosis(
        self,
        clinical_note_id: UUID,
        cie10_code: str,
        description: str,
        diagnosis_type: str = "principal"
    ) -> Diagnosis:
        """Create a new diagnosis."""
        diagnosis = Diagnosis(
            clinical_note_id=clinical_note_id,
            cie10_code=cie10_code.upper(),
            description=description,
            diagnosis_type=diagnosis_type
        )
        self.db.add(diagnosis)
        await self.db.flush()
        await self.db.refresh(diagnosis)

        logger.info(f"Diagnosis created: {diagnosis.id}")
        return diagnosis

    async def get_diagnoses_by_clinical_note(
        self, clinical_note_id: UUID
    ) -> List[Diagnosis]:
        """Get diagnoses for a clinical note."""
        result = await self.db.execute(
            select(Diagnosis)
            .where(Diagnosis.clinical_note_id == clinical_note_id)
            .order_by(Diagnosis.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_most_frequent_diagnoses(
        self,
        limit: int = 10,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Tuple[str, int]]:
        """Get most frequent CIE-10 diagnoses."""
        query = (
            select(Diagnosis.cie10_code, func.count(Diagnosis.id).label("count"))
            .group_by(Diagnosis.cie10_code)
            .order_by(func.count(Diagnosis.id).desc())
            .limit(limit)
        )

        if date_from:
            query = query.where(Diagnosis.created_at >= date_from)
        if date_to:
            query = query.where(Diagnosis.created_at <= date_to)

        result = await self.db.execute(query)
        return list(result.all())


class MedicalDocumentService:
    """Service for managing medical documents."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(
        self,
        clinical_note_id: UUID,
        file_name: str,
        file_type: str,
        file_path: str,
        file_size: Optional[int] = None,
        description: Optional[str] = None,
        uploaded_by: Optional[UUID] = None
    ) -> MedicalDocument:
        """Create a document record."""
        valid_types = ["pdf", "jpeg", "jpg", "png", "dicom"]
        if file_type.lower() not in valid_types:
            raise ValidationException(
                f"Invalid file type. Allowed: {', '.join(valid_types)}"
            )

        document = MedicalDocument(
            clinical_note_id=clinical_note_id,
            file_name=file_name,
            file_type=file_type.lower(),
            file_path=file_path,
            file_size=file_size,
            description=description,
            uploaded_by=uploaded_by
        )
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)

        logger.info(f"Medical document created: {document.id}")
        return document

    async def get_documents_by_clinical_note(
        self, clinical_note_id: UUID
    ) -> List[MedicalDocument]:
        """Get documents for a clinical note."""
        result = await self.db.execute(
            select(MedicalDocument)
            .where(MedicalDocument.clinical_note_id == clinical_note_id)
            .order_by(MedicalDocument.created_at.desc())
        )
        return list(result.scalars().all())
