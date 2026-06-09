from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class EvolutionCreate(BaseModel):
    observations: str

class EvolutionResponse(BaseModel):
    id: UUID
    record_id: UUID
    doctor_id: UUID
    observations: str
    created_at: datetime

class PrescriptionCreate(BaseModel):
    medication: str = Field(..., min_length=2)
    dosage: str = Field(..., min_length=1)
    frequency: str = Field(..., min_length=1)
    duration: str = Field(..., min_length=1)
    evolution_id: Optional[UUID] = Field(None, alias="evolutionId")

class PrescriptionResponse(BaseModel):
    id: UUID
    record_id: UUID
    doctor_id: UUID
    medication: str
    dosage: str
    frequency: str
    duration: str
    created_at: datetime

class AttachmentResponse(BaseModel):
    id: UUID
    record_id: UUID
    evolution_id: UUID
    doctor_id: UUID
    filename: str
    content_type: str
    file_size: int
    created_at: datetime

class MedicalRecordResponse(BaseModel):
    record_id: UUID
    patient_id: UUID
    evolutions: List[EvolutionResponse]
    prescriptions: List[PrescriptionResponse] = []
    attachments: List[AttachmentResponse] = []
