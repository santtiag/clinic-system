from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import SessionLocal
from src.presentation.schemas import (
    InvoiceCreateRequest, InvoiceResponse,
    PaymentRequest, PaymentResponse,
    RefundRequest, RefundResponse,
)
from src.application.services import BillingService
from src.presentation.dependencies import get_current_user

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/invoices", status_code=status.HTTP_201_CREATED, response_model=InvoiceResponse)
async def create_invoice(
    payload: InvoiceCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "staff"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    service = BillingService(db)
    inv = await service.generate_invoice(
        appointment_id=payload.appointment_id,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        amount=payload.amount,
        description=payload.description,
    )
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

@router.get("/invoices/pending", response_model=List[InvoiceResponse])
async def list_pending(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BillingService(db)
    invoices = await service.list_pending_invoices()
    return [
        InvoiceResponse(
            id=i.id,
            appointment_id=i.appointment_id,
            patient_id=i.patient_id,
            doctor_id=i.doctor_id,
            amount=float(i.amount),
            status=i.status.value,
            description=i.description,
            created_at=i.created_at,
        ) for i in invoices
    ]

@router.post("/payments", status_code=status.HTTP_201_CREATED, response_model=PaymentResponse)
async def process_payment(
    payload: PaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BillingService(db)
    pay = await service.process_payment(
        invoice_id=payload.invoice_id,
        amount=payload.amount,
        method=payload.method,
        transaction_ref=payload.transaction_ref or "TX-MOCK",
    )
    return PaymentResponse(
        id=pay.id,
        invoice_id=pay.invoice_id,
        amount=float(pay.amount),
        method=pay.method.value,
        status=pay.status.value,
        transaction_ref=pay.transaction_ref,
        created_at=pay.created_at,
    )

@router.post("/refunds", status_code=status.HTTP_201_CREATED, response_model=RefundResponse)
async def process_refund(
    payload: RefundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "staff"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
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
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "staff"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    service = BillingService(db)
    invoices = await service.list_invoices(status)
    return [
        InvoiceResponse(
            id=i.id,
            appointment_id=i.appointment_id,
            patient_id=i.patient_id,
            doctor_id=i.doctor_id,
            amount=float(i.amount),
            status=i.status.value,
            description=i.description,
            created_at=i.created_at,
        ) for i in invoices
    ]
