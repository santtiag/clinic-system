from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class AvailabilitySlotResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None

class AppointmentCreate(BaseModel):
    slot_id: UUID
    reason: Optional[str] = Field(None, max_length=255)
    patient_id: Optional[UUID] = Field(None, alias="patientId")

class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    slot_id: UUID
    status: str
    reason: Optional[str]
    created_at: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None

class RescheduleRequest(BaseModel):
    new_slot_id: UUID

class AssignDoctorRequest(BaseModel):
    doctor_id: UUID = Field(..., alias="doctorId")

class DoctorResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    specialty: str

class StatusUpdateRequest(BaseModel):
    status: str


class StatusHistoryResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    old_status: Optional[str]
    new_status: str
    changed_by: Optional[UUID]
    changed_by_role: Optional[str]
    changed_at: datetime
