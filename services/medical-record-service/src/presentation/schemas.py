"""
Presentation schemas for Medical Record Service.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field

from common.schemas import BaseSchema


class MedicalRecordCreate(BaseSchema):
    patient_id: str = Field(description="Patient ID")


class MedicalRecordResponse(BaseSchema):
    id: UUID
    patient_id: UUID = Field(alias="patientId")
    record_number: str = Field(alias="recordNumber")
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ClinicalNoteCreate(BaseSchema):
    medical_record_id: str = Field(alias="medicalRecordId")
    doctor_id: str = Field(alias="doctorId")
    appointment_id: Optional[str] = Field(default=None, alias="appointmentId")
    note_type: str = Field(default="consultation", alias="noteType")
    chief_complaint: Optional[str] = Field(default=None, alias="chiefComplaint")
    present_illness: Optional[str] = Field(default=None, alias="presentIllness")
    physical_exam: Optional[str] = Field(default=None, alias="physicalExam")
    evolution: Optional[str] = None
    observations: Optional[str] = None


class ClinicalNoteResponse(BaseSchema):
    id: UUID
    medical_record_id: UUID = Field(alias="medicalRecordId")
    doctor_id: UUID = Field(alias="doctorId")
    appointment_id: Optional[UUID] = Field(default=None, alias="appointmentId")
    note_type: str = Field(alias="noteType")
    chief_complaint: Optional[str] = Field(default=None, alias="chiefComplaint")
    present_illness: Optional[str] = Field(default=None, alias="presentIllness")
    physical_exam: Optional[str] = Field(default=None, alias="physicalExam")
    evolution: Optional[str] = None
    observations: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class DiagnosisCreate(BaseSchema):
    clinical_note_id: str = Field(alias="clinicalNoteId")
    cie10_code: str = Field(alias="cie10Code", min_length=1, max_length=10)
    description: str
    diagnosis_type: str = Field(default="principal", alias="diagnosisType")


class DiagnosisResponse(BaseSchema):
    id: UUID
    clinical_note_id: UUID = Field(alias="clinicalNoteId")
    cie10_code: str = Field(alias="cie10Code")
    description: str
    diagnosis_type: str = Field(alias="diagnosisType")
    created_at: datetime = Field(alias="createdAt")


class PrescriptionCreate(BaseSchema):
    clinical_note_id: str = Field(alias="clinicalNoteId")
    medication_name: str = Field(alias="medicationName", min_length=1)
    dosage: str
    frequency: str
    duration: str
    route: Optional[str] = None
    instructions: Optional[str] = None


class PrescriptionResponse(BaseSchema):
    id: UUID
    clinical_note_id: UUID = Field(alias="clinicalNoteId")
    medication_name: str = Field(alias="medicationName")
    dosage: str
    frequency: str
    duration: str
    route: Optional[str] = None
    instructions: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")


class MedicalDocumentCreate(BaseSchema):
    clinical_note_id: str = Field(alias="clinicalNoteId")
    file_name: str = Field(alias="fileName")
    file_type: str = Field(alias="fileType")
    file_path: str = Field(alias="filePath")
    file_size: Optional[int] = Field(default=None, alias="fileSize")
    description: Optional[str] = None


class MedicalDocumentResponse(BaseSchema):
    id: UUID
    clinical_note_id: UUID = Field(alias="clinicalNoteId")
    file_name: str = Field(alias="fileName")
    file_type: str = Field(alias="fileType")
    file_path: str = Field(alias="filePath")
    file_size: Optional[int] = Field(default=None, alias="fileSize")
    description: Optional[str] = None
    uploaded_by: Optional[UUID] = Field(default=None, alias="uploadedBy")
    created_at: datetime = Field(alias="createdAt")


class ClinicalNoteDetailResponse(ClinicalNoteResponse):
    diagnoses: List[DiagnosisResponse] = []
    prescriptions: List[PrescriptionResponse] = []
    documents: List[MedicalDocumentResponse] = []


class MedicalRecordDetailResponse(MedicalRecordResponse):
    clinical_notes: List[ClinicalNoteDetailResponse] = Field(default=[], alias="clinicalNotes")


class ClinicalNoteListResponse(BaseSchema):
    items: List[ClinicalNoteResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class PrescriptionListResponse(BaseSchema):
    items: List[PrescriptionResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class FrequentDiagnosisResponse(BaseSchema):
    cie10_code: str = Field(alias="cie10Code")
    count: int


class TimelineEntry(BaseSchema):
    date: datetime
    type: str
    title: str
    description: Optional[str] = None
    doctor_id: Optional[UUID] = Field(default=None, alias="doctorId")
