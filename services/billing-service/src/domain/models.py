from datetime import datetime
from enum import Enum
from uuid import UUID

class InvoiceStatus(str, Enum):
    PENDING = "pendiente"
    PAID = "pagado"
    FAILED = "fallido"
    CANCELLED = "cancelado"
    REFUNDED = "reembolsado"

class PaymentMethod(str, Enum):
    CARD = "tarjeta"
    CASH = "efectivo"
    TRANSFER = "transferencia"

class PaymentStatus(str, Enum):
    PENDING = "pendiente"
    COMPLETED = "completado"
    FAILED = "fallido"

class RefundStatus(str, Enum):
    PENDING = "pendiente"
    COMPLETED = "completado"
    REJECTED = "rechazado"

class Invoice:
    def __init__(self, invoice_id: UUID, appointment_id: UUID, patient_id: UUID,
                 doctor_id: UUID, amount: float, status: InvoiceStatus,
                 description: str, created_at: datetime):
        self.invoice_id = invoice_id
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.amount = amount
        self.status = status
        self.description = description
        self.created_at = created_at
