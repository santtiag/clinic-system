import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database import Base
from src.domain.models import InvoiceStatus, PaymentMethod, PaymentStatus, RefundStatus

class InvoiceORM(Base):
    __tablename__ = "invoices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SAEnum(InvoiceStatus, name="invoice_status_enum",
               values_callable=lambda x: [e.value for e in x]),
        default=InvoiceStatus.PENDING, nullable=False,
    )
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class PaymentORM(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(
        SAEnum(PaymentMethod, name="payment_method_enum",
               values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    status = Column(
        SAEnum(PaymentStatus, name="payment_status_enum",
               values_callable=lambda x: [e.value for e in x]),
        default=PaymentStatus.PENDING, nullable=False,
    )
    transaction_ref = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class RefundORM(Base):
    __tablename__ = "refunds"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(
        SAEnum(RefundStatus, name="refund_status_enum",
               values_callable=lambda x: [e.value for e in x]),
        default=RefundStatus.PENDING, nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
