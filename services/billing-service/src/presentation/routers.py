from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import SessionLocal
from src.presentation.schemas import (
    InvoiceCreateRequest, InvoiceResponse,
    PaymentRequest, PaymentResponse,
    RefundRequest, RefundResponse,
)
from src.application.services import BillingService
from src.presentation.dependencies import get_current_user, require_staff

router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session


def _invoice_response(inv) -> InvoiceResponse:
    return InvoiceResponse(
        id=inv.id,
        appointment_id=inv.appointment_id,
        patient_id=inv.patient_id,
        doctor_id=inv.doctor_id,
        amount=float(inv.amount),
        status=inv.status.value,
        description=inv.description,
        created_at=inv.created_at,
    )


def _payment_response(pay) -> PaymentResponse:
    return PaymentResponse(
        id=pay.id,
        invoice_id=pay.invoice_id,
        amount=float(pay.amount),
        method=pay.method.value,
        status=pay.status.value,
        transaction_ref=pay.transaction_ref,
        created_at=pay.created_at,
    )


@router.post("/invoices", status_code=status.HTTP_201_CREATED, response_model=InvoiceResponse)
async def create_invoice(
    payload: InvoiceCreateRequest,
    db: AsyncSession = Depends(get_db),
    _staff: dict = Depends(require_staff),
):
    service = BillingService(db)
    inv = await service.generate_invoice(
        appointment_id=payload.appointment_id,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        amount=payload.amount,
        description=payload.description,
    )
    return _invoice_response(inv)


@router.get("/invoices/me", response_model=List[InvoiceResponse])
async def my_invoices(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "patient":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only patients can view their invoices")
    service = BillingService(db)
    invoices = await service.list_patient_invoices(UUID(current_user["user_id"]), status)
    return [_invoice_response(i) for i in invoices]


@router.get("/invoices/pending", response_model=List[InvoiceResponse])
async def list_pending(
    db: AsyncSession = Depends(get_db),
    _staff: dict = Depends(require_staff),
):
    service = BillingService(db)
    invoices = await service.list_pending_invoices()
    return [_invoice_response(i) for i in invoices]


@router.post("/payments", status_code=status.HTTP_201_CREATED, response_model=PaymentResponse)
async def process_payment(
    payload: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    role = current_user.get("role")
    if role not in ("patient", "staff", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    service = BillingService(db)
    patient_id = UUID(current_user["user_id"]) if role == "patient" else None
    pay = await service.process_payment(
        invoice_id=payload.invoice_id,
        amount=payload.amount,
        method=payload.method,
        transaction_ref=payload.transaction_ref or "TX-MOCK",
        patient_id=patient_id,
        user_role=role,
    )
    return _payment_response(pay)


@router.get("/invoices/{invoice_id}/payments", response_model=List[PaymentResponse])
async def list_invoice_payments(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    _staff: dict = Depends(require_staff),
):
    service = BillingService(db)
    payments = await service.list_invoice_payments(invoice_id)
    return [_payment_response(p) for p in payments]


@router.post("/refunds", status_code=status.HTTP_201_CREATED, response_model=RefundResponse)
async def process_refund(
    payload: RefundRequest,
    db: AsyncSession = Depends(get_db),
    _staff: dict = Depends(require_staff),
):
    service = BillingService(db)
    ref = await service.process_refund(
        payment_id=payload.payment_id,
        amount=payload.amount,
        reason=payload.reason,
    )
    return RefundResponse(
        id=ref.id,
        payment_id=ref.payment_id,
        amount=float(ref.amount),
        reason=ref.reason,
        status=ref.status.value,
        created_at=ref.created_at,
    )


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _staff: dict = Depends(require_staff),
):
    service = BillingService(db)
    invoices = await service.list_invoices(status)
    return [_invoice_response(i) for i in invoices]


@router.get("/invoices/{invoice_id}/receipt.pdf")
async def download_receipt(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BillingService(db)
    inv = await service.get_invoice(invoice_id)
    role = current_user.get("role")
    if role == "patient" and str(inv.patient_id) != current_user.get("user_id"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    if role not in ("patient", "staff", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    pdf_bytes = service.generate_receipt_pdf(inv)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{invoice_id}.pdf"},
    )
