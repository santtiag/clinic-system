from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field

class InvoiceCreateRequest(BaseModel):
    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    amount: Optional[float] = Field(None, ge=0)
    description: Optional[str] = "Consulta médica"

class InvoiceResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    amount: float
    status: str
    description: Optional[str]
    created_at: datetime

class PaymentRequest(BaseModel):
    invoice_id: UUID
    amount: float = Field(..., ge=0)
    method: str
    transaction_ref: Optional[str] = "TX-MOCK"

class PaymentResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    amount: float
    method: str
    status: str
    transaction_ref: Optional[str]
    created_at: datetime

class RefundRequest(BaseModel):
    payment_id: UUID
    amount: float = Field(..., ge=0)
    reason: Optional[str]

class RefundResponse(BaseModel):
    id: UUID
    payment_id: UUID
    amount: float
    reason: Optional[str]
    status: str
    created_at: datetime
