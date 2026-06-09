"""
Presentation schemas for Billing Service.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field

from common.schemas import BaseSchema


class InvoiceLineItemCreate(BaseSchema):
    description: str
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(alias="unitPrice", ge=0)
    total_price: float = Field(alias="totalPrice", ge=0)


class InvoiceLineItemResponse(BaseSchema):
    id: UUID
    invoice_id: UUID = Field(alias="invoiceId")
    description: str
    quantity: int
    unit_price: float = Field(alias="unitPrice")
    total_price: float = Field(alias="totalPrice")


class InvoiceCreate(BaseSchema):
    patient_id: str = Field(alias="patientId")
    appointment_id: str = Field(alias="appointmentId")
    doctor_id: str = Field(alias="doctorId")
    consultation_fee: float = Field(alias="consultationFee", ge=0)
    line_items: Optional[List[InvoiceLineItemCreate]] = Field(default=None, alias="lineItems")
    notes: Optional[str] = None


class InvoiceResponse(BaseSchema):
    id: UUID
    invoice_number: str = Field(alias="invoiceNumber")
    patient_id: UUID = Field(alias="patientId")
    appointment_id: UUID = Field(alias="appointmentId")
    doctor_id: UUID = Field(alias="doctorId")
    subtotal: float
    tax: float
    total: float
    status: str
    notes: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    paid_at: Optional[datetime] = Field(default=None, alias="paidAt")


class InvoiceDetailResponse(InvoiceResponse):
    line_items: List[InvoiceLineItemResponse] = Field(default=[], alias="lineItems")
    payments: List["PaymentResponse"] = []


class InvoiceListResponse(BaseSchema):
    items: List[InvoiceResponse]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class PaymentCreate(BaseSchema):
    invoice_id: str = Field(alias="invoiceId")
    amount: float = Field(ge=0)
    method: str = Field(default="cash")
    transaction_reference: Optional[str] = Field(default=None, alias="transactionReference")


class PaymentResponse(BaseSchema):
    id: UUID
    invoice_id: UUID = Field(alias="invoiceId")
    amount: float
    method: str
    status: str
    transaction_reference: Optional[str] = Field(default=None, alias="transactionReference")
    notes: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    refunded_at: Optional[datetime] = Field(default=None, alias="refundedAt")


class RefundRequest(BaseSchema):
    reason: Optional[str] = None


class RevenueReportRequest(BaseSchema):
    date_from: Optional[datetime] = Field(default=None, alias="dateFrom")
    date_to: Optional[datetime] = Field(default=None, alias="dateTo")
    doctor_id: Optional[str] = Field(default=None, alias="doctorId")


class RevenueReportResponse(BaseSchema):
    total_revenue: float = Field(alias="totalRevenue")
    total_invoices: int = Field(alias="totalInvoices")
    paid_invoices: int = Field(alias="paidInvoices")
    pending_invoices: int = Field(alias="pendingInvoices")
    refunded_invoices: int = Field(alias="refundedInvoices")
    period: str


class DoctorRevenueItem(BaseSchema):
    doctor_id: UUID = Field(alias="doctorId")
    doctor_name: str = Field(alias="doctorName")
    total_revenue: float = Field(alias="totalRevenue")
    invoice_count: int = Field(alias="invoiceCount")


class PendingPaymentReport(BaseSchema):
    invoice_id: UUID = Field(alias="invoiceId")
    invoice_number: str = Field(alias="invoiceNumber")
    patient_id: UUID = Field(alias="patientId")
    total: float
    status: str
    created_at: datetime = Field(alias="createdAt")
    days_overdue: int = Field(alias="daysOverdue")
