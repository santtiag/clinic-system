from datetime import datetime
from uuid import UUID
from typing import List
from pydantic import BaseModel

class EvolutionCreate(BaseModel):
    observations: str

class EvolutionResponse(BaseModel):
    id: UUID
    record_id: UUID
    doctor_id: UUID
    observations: str
    created_at: datetime

class MedicalRecordResponse(BaseModel):
    record_id: UUID
    patient_id: UUID
    evolutions: List[EvolutionResponse]
