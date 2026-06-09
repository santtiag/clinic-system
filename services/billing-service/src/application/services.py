from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from src.infrastructure.models import InvoiceORM
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories import InvoiceRepository, PaymentRepository, RefundRepository
from src.domain.models import InvoiceStatus, RefundStatus

class BillingService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._invoices = InvoiceRepository(session)
        self._payments = PaymentRepository(session)
        self._refunds = RefundRepository(session)

    async def generate_invoice(self, appointment_id: UUID, patient_id: UUID, doctor_id: UUID,
                               amount: Optional[float] = None, description: str = "Consulta médica"):
        existing = await self._invoices.get_by_appointment(appointment_id)
        if existing:
            return existing
        amt = Decimal(str(amount)) if amount else Decimal("50.00")
        return await self._invoices.create(appointment_id, patient_id, doctor_id, amt, description)

    async def list_pending_invoices(self) -> List[InvoiceORM]:
        return await self._invoices.list_pending()

    async def process_payment(self, invoice_id: UUID, amount: float, method: str,
                              transaction_ref: str = "TX-MOCK"):
        inv = await self._invoices.get_by_id(invoice_id)
        if not inv:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invoice not found")
        if inv.status != InvoiceStatus.PENDING:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Invoice is {inv.status.value}")

        pay = await self._payments.create(invoice_id, Decimal(str(amount)), method, transaction_ref)
        if Decimal(str(amount)) >= inv.amount:
            await self._invoices.update_status(invoice_id, InvoiceStatus.PAID)
        return pay

    async def process_refund(self, payment_id: UUID, amount: float, reason: Optional[str]):
        payment = await self._payments.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")

        ref = await self._refunds.create(payment_id, Decimal(str(amount)), reason or "")
        await self._invoices.update_status(payment.invoice_id, InvoiceStatus.REFUNDED)
        return ref

    async def list_invoices(self, status: Optional[str] = None):
        return await self._invoices.list_all(status)
