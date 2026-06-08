"""
Domain entities for Billing Service.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum

from sqlalchemy import (
    Column, String, DateTime, Boolean, Enum as SQLEnum,
    ForeignKey, Numeric, Text, Integer, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from common.database import BaseModel


class InvoiceStatus(str, Enum):
    """Invoice status."""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Payment status."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method."""
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"


class Invoice(BaseModel):
    """Invoice / Receipt model."""
    __tablename__ = "invoices"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_number = Column(String(50), unique=True, nullable=False)
    patient_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    appointment_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    doctor_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.PENDING)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    # Relationships
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_invoices_patient", "patient_id"),
        Index("ix_invoices_status", "status"),
    )


class InvoiceLineItem(BaseModel):
    """Invoice line item."""
    __tablename__ = "invoice_line_items"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_id = Column(PGUUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")


class Payment(BaseModel):
    """Payment record."""
    __tablename__ = "payments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_id = Column(PGUUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(SQLEnum(PaymentMethod), nullable=False, default=PaymentMethod.CASH)
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    transaction_reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    refunded_at = Column(DateTime, nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")

    __table_args__ = (
        Index("ix_payments_invoice", "invoice_id"),
        Index("ix_payments_status", "status"),
    )
