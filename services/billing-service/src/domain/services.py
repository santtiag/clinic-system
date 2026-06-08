"""
Domain services for Billing Service.
"""

from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.exceptions import NotFoundException, ValidationException, ConflictException
from common.logging import get_logger

from src.domain.entities import Invoice, InvoiceLineItem, Payment, InvoiceStatus, PaymentStatus, PaymentMethod


logger = get_logger(__name__)


class InvoiceService:
    """Service for managing invoices/receipts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_invoice(
        self,
        patient_id: UUID,
        appointment_id: UUID,
        doctor_id: UUID,
        consultation_fee: float,
        line_items: Optional[List[dict]] = None,
        notes: Optional[str] = None
    ) -> Invoice:
        """Generate an invoice automatically after appointment completion."""
        # Check if invoice already exists for this appointment
        result = await self.db.execute(
            select(Invoice).where(Invoice.appointment_id == appointment_id)
        )
        if result.scalar_one_or_none():
            raise ConflictException(f"Invoice already exists for appointment {appointment_id}")

        # Generate invoice number
        invoice_number = f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(appointment_id)[:4].upper()}"

        # Calculate totals
        subtotal = Decimal(str(consultation_fee))
        tax = subtotal * Decimal("0.18")  # 18% IGV
        total = subtotal + tax

        # Add line items if provided
        if line_items:
            for item in line_items:
                subtotal += Decimal(str(item.get("total_price", 0)))
            tax = subtotal * Decimal("0.18")
            total = subtotal + tax

        invoice = Invoice(
            invoice_number=invoice_number,
            patient_id=patient_id,
            appointment_id=appointment_id,
            doctor_id=doctor_id,
            subtotal=subtotal,
            tax=tax,
            total=total,
            status=InvoiceStatus.PENDING,
            notes=notes
        )
        self.db.add(invoice)
        await self.db.flush()
        await self.db.refresh(invoice)

        # Add consultation line item
        line_item = InvoiceLineItem(
            invoice_id=invoice.id,
            description="Consulta médica",
            quantity=1,
            unit_price=Decimal(str(consultation_fee)),
            total_price=Decimal(str(consultation_fee))
        )
        self.db.add(line_item)

        # Add additional line items
        if line_items:
            for item in line_items:
                additional_line = InvoiceLineItem(
                    invoice_id=invoice.id,
                    description=item.get("description", "Servicio adicional"),
                    quantity=item.get("quantity", 1),
                    unit_price=Decimal(str(item.get("unit_price", 0))),
                    total_price=Decimal(str(item.get("total_price", 0)))
                )
                self.db.add(additional_line)

        await self.db.flush()
        await self.db.refresh(invoice)

        logger.info(f"Invoice generated: {invoice.id} for appointment {appointment_id}")
        return invoice

    async def get_invoice(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get invoice by ID with line items and payments."""
        result = await self.db.execute(
            select(Invoice)
            .options(
                selectinload(Invoice.line_items),
                selectinload(Invoice.payments)
            )
            .where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()

    async def get_invoices_by_patient(
        self,
        patient_id: UUID,
        status: Optional[InvoiceStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Invoice], int]:
        """Get invoices for a patient."""
        offset = (page - 1) * page_size

        query = select(Invoice).where(Invoice.patient_id == patient_id)
        if status:
            query = query.where(Invoice.status == status)

        count_result = await self.db.execute(
            select(func.count(Invoice.id)).where(Invoice.patient_id == patient_id)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            query.options(selectinload(Invoice.line_items))
            .order_by(Invoice.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        invoices = list(result.scalars().all())

        return invoices, total

    async def get_pending_invoices(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Invoice], int]:
        """Get all pending invoices (for admin)."""
        offset = (page - 1) * page_size

        count_result = await self.db.execute(
            select(func.count(Invoice.id)).where(Invoice.status == InvoiceStatus.PENDING)
        )
        total = count_result.scalar()

        result = await self.db.execute(
            select(Invoice)
            .options(selectinload(Invoice.line_items))
            .where(Invoice.status == InvoiceStatus.PENDING)
            .order_by(Invoice.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        invoices = list(result.scalars().all())

        return invoices, total

    async def cancel_invoice(self, invoice_id: UUID, reason: Optional[str] = None) -> Invoice:
        """Cancel an invoice."""
        invoice = await self.get_invoice(invoice_id)
        if not invoice:
            raise NotFoundException("Invoice", invoice_id)

        if invoice.status == InvoiceStatus.PAID:
            raise ValidationException("Cannot cancel a paid invoice. Process refund instead.")

        invoice.status = InvoiceStatus.CANCELLED
        invoice.updated_at = datetime.now(timezone.utc)
        if reason:
            invoice.notes = f"{invoice.notes or ''}\nCancelled: {reason}"

        await self.db.flush()
        logger.info(f"Invoice cancelled: {invoice_id}")
        return invoice


class PaymentService:
    """Service for managing payments (mock implementation)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_payment(
        self,
        invoice_id: UUID,
        amount: float,
        method: PaymentMethod = PaymentMethod.CASH,
        transaction_reference: Optional[str] = None
    ) -> Payment:
        """
        Process a payment (mock - always succeeds).
        In production, this would integrate with a payment gateway.
        """
        invoice = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id)
        )
        invoice = invoice.scalar_one_or_none()
        if not invoice:
            raise NotFoundException("Invoice", invoice_id)

        if invoice.status == InvoiceStatus.PAID:
            raise ConflictException("Invoice is already paid")

        if invoice.status == InvoiceStatus.CANCELLED:
            raise ValidationException("Cannot process payment for cancelled invoice")

        # Create payment record
        payment = Payment(
            invoice_id=invoice_id,
            amount=Decimal(str(amount)),
            method=method,
            status=PaymentStatus.PAID,  # Mock: always succeeds
            transaction_reference=transaction_reference or f"MOCK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        )
        self.db.add(payment)

        # Update invoice status
        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.now(timezone.utc)
        invoice.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(payment)

        logger.info(f"Payment processed: {payment.id} for invoice {invoice_id}")
        return payment

    async def process_refund(
        self,
        payment_id: UUID,
        reason: Optional[str] = None
    ) -> Payment:
        """Process a refund (mock)."""
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.invoice))
            .where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise NotFoundException("Payment", payment_id)

        if payment.status != PaymentStatus.PAID:
            raise ValidationException("Cannot refund a payment that is not paid")

        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        payment.updated_at = datetime.now(timezone.utc)
        payment.refunded_at = datetime.now(timezone.utc)
        if reason:
            payment.notes = f"{payment.notes or ''}\nRefund: {reason}"

        # Update invoice status
        payment.invoice.status = InvoiceStatus.REFUNDED
        payment.invoice.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        logger.info(f"Payment refunded: {payment_id}")
        return payment

    async def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """Get payment by ID."""
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.invoice))
            .where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_payments_by_invoice(self, invoice_id: UUID) -> List[Payment]:
        """Get payments for an invoice."""
        result = await self.db.execute(
            select(Payment)
            .where(Payment.invoice_id == invoice_id)
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())
