import io
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

    async def list_patient_invoices(self, patient_id: UUID, status: Optional[str] = None):
        return await self._invoices.list_by_patient(patient_id, status)

    async def process_payment(
        self,
        invoice_id: UUID,
        amount: float,
        method: str,
        transaction_ref: str = "TX-MOCK",
        patient_id: UUID | None = None,
        user_role: str | None = None,
    ):
        inv = await self._invoices.get_by_id(invoice_id)
        if not inv:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invoice not found")
        if user_role == "patient" and inv.patient_id != patient_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot pay another patient's invoice")
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
        inv = await self._invoices.get_by_id(payment.invoice_id)
        if not inv or inv.status != InvoiceStatus.PAID:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only paid invoices can be refunded")

        ref = await self._refunds.create(payment_id, Decimal(str(amount)), reason or "")
        await self._invoices.update_status(payment.invoice_id, InvoiceStatus.REFUNDED)
        return ref

    async def list_invoices(self, status: Optional[str] = None):
        return await self._invoices.list_all(status)

    async def get_invoice(self, invoice_id: UUID) -> InvoiceORM:
        inv = await self._invoices.get_by_id(invoice_id)
        if not inv:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Invoice not found")
        return inv

    def generate_receipt_pdf(self, invoice: InvoiceORM) -> bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            content = (
                f"RECIBO DE PAGO\n"
                f"Factura: {invoice.id}\n"
                f"Paciente: {invoice.patient_id}\n"
                f"Médico: {invoice.doctor_id}\n"
                f"Monto: ${invoice.amount}\n"
                f"Estado: {invoice.status.value}\n"
                f"Descripción: {invoice.description}\n"
            )
            return content.encode("utf-8")

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, 750, "Recibo de Pago - Clínica")
        pdf.setFont("Helvetica", 12)
        y = 710
        lines = [
            f"Factura ID: {invoice.id}",
            f"Cita ID: {invoice.appointment_id}",
            f"Paciente ID: {invoice.patient_id}",
            f"Médico ID: {invoice.doctor_id}",
            f"Monto: ${invoice.amount}",
            f"Estado: {invoice.status.value}",
            f"Descripción: {invoice.description or 'Consulta médica'}",
            f"Fecha: {invoice.created_at.isoformat()}",
        ]
        for line in lines:
            pdf.drawString(72, y, line)
            y -= 24
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer.read()
