"""
Invoice and Payment routers.
"""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordBearer

from common.database import get_db
from common.security import decode_token
from common.exceptions import UnauthorizedException

from src.domain.services import InvoiceService, PaymentService
from src.domain.entities import InvoiceStatus
from src.presentation.schemas import (
    InvoiceCreate, InvoiceResponse, InvoiceDetailResponse,
    InvoiceListResponse, PaymentCreate, PaymentResponse,
    RefundRequest, RevenueReportResponse, DoctorRevenueItem,
    PendingPaymentReport, InvoiceLineItemResponse
)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise UnauthorizedException("Missing authentication")
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")
    return payload


def _to_invoice_response(inv) -> InvoiceResponse:
    return InvoiceResponse(
        id=inv.id,
        invoiceNumber=inv.invoice_number,
        patientId=inv.patient_id,
        appointmentId=inv.appointment_id,
        doctorId=inv.doctor_id,
        subtotal=float(inv.subtotal),
        tax=float(inv.tax),
        total=float(inv.total),
        status=inv.status.value,
        notes=inv.notes,
        createdAt=inv.created_at,
        updatedAt=inv.updated_at,
        paidAt=inv.paid_at
    )


def _to_payment_response(p) -> PaymentResponse:
    return PaymentResponse(
        id=p.id,
        invoiceId=p.invoice_id,
        amount=float(p.amount),
        method=p.method.value,
        status=p.status.value,
        transactionReference=p.transaction_reference,
        notes=p.notes,
        createdAt=p.created_at,
        updatedAt=p.updated_at,
        refundedAt=p.refunded_at
    )


# ====================
# INVOICES
# ====================

@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: InvoiceCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Generate a new invoice."""
    service = InvoiceService(db)
    line_items = [
        {
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price
        }
        for item in request.line_items
    ] if request.line_items else None

    invoice = await service.generate_invoice(
        patient_id=UUID(request.patient_id),
        appointment_id=UUID(request.appointment_id),
        doctor_id=UUID(request.doctor_id),
        consultation_fee=request.consultation_fee,
        line_items=line_items,
        notes=request.notes
    )
    return _to_invoice_response(invoice)


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(
    invoice_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get invoice with line items and payments."""
    service = InvoiceService(db)
    invoice = await service.get_invoice(invoice_id)
    if not invoice:
        from common.exceptions import NotFoundException
        raise NotFoundException("Invoice", invoice_id)

    return InvoiceDetailResponse(
        id=invoice.id,
        invoiceNumber=invoice.invoice_number,
        patientId=invoice.patient_id,
        appointmentId=invoice.appointment_id,
        doctorId=invoice.doctor_id,
        subtotal=float(invoice.subtotal),
        tax=float(invoice.tax),
        total=float(invoice.total),
        status=invoice.status.value,
        notes=invoice.notes,
        createdAt=invoice.created_at,
        updatedAt=invoice.updated_at,
        paidAt=invoice.paid_at,
        lineItems=[
            InvoiceLineItemResponse(
                id=li.id,
                invoiceId=li.invoice_id,
                description=li.description,
                quantity=li.quantity,
                unitPrice=float(li.unit_price),
                totalPrice=float(li.total_price)
            )
            for li in invoice.line_items
        ],
        payments=[_to_payment_response(p) for p in invoice.payments]
    )


@router.get("/patient/{patient_id}", response_model=InvoiceListResponse)
async def get_patient_invoices(
    patient_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get invoices for a patient."""
    service = InvoiceService(db)
    status_enum = InvoiceStatus(status_filter) if status_filter else None
    invoices, total = await service.get_invoices_by_patient(patient_id, status_enum, page, page_size)

    return InvoiceListResponse(
        items=[_to_invoice_response(inv) for inv in invoices],
        total=total,
        page=page,
        pageSize=page_size
    )


@router.get("/pending/all", response_model=InvoiceListResponse)
async def get_pending_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get all pending invoices (admin)."""
    service = InvoiceService(db)
    invoices, total = await service.get_pending_invoices(page, page_size)

    return InvoiceListResponse(
        items=[_to_invoice_response(inv) for inv in invoices],
        total=total,
        page=page,
        pageSize=page_size
    )


@router.post("/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(
    invoice_id: UUID,
    reason: Optional[str] = Query(None),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Cancel an invoice."""
    service = InvoiceService(db)
    invoice = await service.cancel_invoice(invoice_id, reason)
    return _to_invoice_response(invoice)


# ====================
# PAYMENTS
# ====================

@router.post("/{invoice_id}/pay", response_model=PaymentResponse)
async def process_payment(
    invoice_id: UUID,
    request: PaymentCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Process a payment for an invoice (mock)."""
    service = PaymentService(db)
    from src.domain.entities import PaymentMethod
    payment = await service.process_payment(
        invoice_id=invoice_id,
        amount=request.amount,
        method=PaymentMethod(request.method),
        transaction_reference=request.transaction_reference
    )
    return _to_payment_response(payment)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get payment by ID."""
    service = PaymentService(db)
    payment = await service.get_payment(payment_id)
    if not payment:
        from common.exceptions import NotFoundException
        raise NotFoundException("Payment", payment_id)
    return _to_payment_response(payment)


@router.post("/payments/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: UUID,
    request: RefundRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Process a refund (mock)."""
    service = PaymentService(db)
    payment = await service.process_refund(payment_id, request.reason)
    return _to_payment_response(payment)


# ====================
# REPORTS
# ====================

@router.get("/reports/revenue", response_model=RevenueReportResponse)
async def get_revenue_report(
    date_from: Optional[datetime] = Query(None, alias="dateFrom"),
    date_to: Optional[datetime] = Query(None, alias="dateTo"),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get revenue report for a period."""
    from sqlalchemy import select, func, and_
    from src.domain.entities import Invoice, Payment

    query = select(Invoice)
    if date_from:
        query = query.where(Invoice.created_at >= date_from)
    if date_to:
        query = query.where(Invoice.created_at <= date_to)

    result = await db.execute(query)
    invoices = result.scalars().all()

    total_revenue = sum(float(inv.total) for inv in invoices)
    paid_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.PAID)
    pending_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.PENDING)
    refunded_count = sum(1 for inv in invoices if inv.status == InvoiceStatus.REFUNDED)

    period = "All time"
    if date_from and date_to:
        period = f"{date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}"

    return RevenueReportResponse(
        totalRevenue=total_revenue,
        totalInvoices=len(invoices),
        paidInvoices=paid_count,
        pendingInvoices=pending_count,
        refundedInvoices=refunded_count,
        period=period
    )


@router.get("/reports/pending", response_model=List[PendingPaymentReport])
async def get_pending_payments_report(
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get report of pending payments (overdue)."""
    from sqlalchemy import select, func
    from src.domain.entities import Invoice

    result = await db.execute(
        select(Invoice)
        .where(Invoice.status == InvoiceStatus.PENDING)
        .order_by(Invoice.created_at.desc())
    )
    invoices = result.scalars().all()

    now = datetime.now(timezone.utc)
    return [
        PendingPaymentReport(
            invoiceId=inv.id,
            invoiceNumber=inv.invoice_number,
            patientId=inv.patient_id,
            total=float(inv.total),
            status=inv.status.value,
            createdAt=inv.created_at,
            daysOverdue=max(0, (now - inv.created_at).days)
        )
        for inv in invoices
    ]
