from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class AvailabilitySlotResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime

class AppointmentCreate(BaseModel):
    slot_id: UUID
    reason: Optional[str] = Field(None, max_length=255)

class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    slot_id: UUID
    status: str
    reason: Optional[str]
    created_at: datetime

class RescheduleRequest(BaseModel):
    new_slot_id: UUID

class StatusUpdateRequest(BaseModel):
    status: str
