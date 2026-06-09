from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import InvoiceORM, PaymentORM, RefundORM
from src.domain.models import InvoiceStatus, PaymentStatus

class InvoiceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, appointment_id: UUID, patient_id: UUID, doctor_id: UUID,
                     amount: Decimal, description: str) -> InvoiceORM:
        inv = InvoiceORM(
            appointment_id=appointment_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            amount=amount,
            description=description,
        )
        self._session.add(inv)
        await self._session.commit()
        await self._session.refresh(inv)
        return inv

    async def get_by_id(self, invoice_id: UUID) -> Optional[InvoiceORM]:
        result = await self._session.execute(
            select(InvoiceORM).where(InvoiceORM.id == invoice_id)
        )
        return result.scalar_one_or_none()

    async def get_by_appointment(self, appointment_id: UUID) -> Optional[InvoiceORM]:
        result = await self._session.execute(
            select(InvoiceORM).where(InvoiceORM.appointment_id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def list_pending(self) -> List[InvoiceORM]:
        result = await self._session.execute(
            select(InvoiceORM)
            .where(InvoiceORM.status == InvoiceStatus.PENDING)
            .order_by(InvoiceORM.created_at.desc())
        )
        return result.scalars().all()
    
    async def list_all(self, status: Optional[str] = None) -> List[InvoiceORM]:
        query = select(InvoiceORM).order_by(InvoiceORM.created_at.desc())
        if status:
            query = query.where(InvoiceORM.status == InvoiceStatus(status))
        result = await self._session.execute(query)
        return result.scalars().all()

    async def list_by_patient(self, patient_id: UUID, status: Optional[str] = None) -> List[InvoiceORM]:
        query = select(InvoiceORM).where(InvoiceORM.patient_id == patient_id).order_by(InvoiceORM.created_at.desc())
        if status:
            query = query.where(InvoiceORM.status == InvoiceStatus(status))
        result = await self._session.execute(query)
        return result.scalars().all()

    async def update_status(self, invoice_id: UUID, status: InvoiceStatus) -> Optional[InvoiceORM]:
        inv = await self.get_by_id(invoice_id)
        if inv:
            inv.status = status
            await self._session.commit()
        return inv


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, invoice_id: UUID, amount: Decimal, method: str,
                     transaction_ref: str) -> PaymentORM:
        pay = PaymentORM(
            invoice_id=invoice_id,
            amount=amount,
            method=method,
            transaction_ref=transaction_ref,
            status=PaymentStatus.COMPLETED,
        )
        self._session.add(pay)
        await self._session.commit()
        await self._session.refresh(pay)
        return pay

    async def get_by_id(self, payment_id: UUID) -> Optional[PaymentORM]:
        result = await self._session.execute(
            select(PaymentORM).where(PaymentORM.id == payment_id)
        )
        return result.scalar_one_or_none()


class RefundRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, payment_id: UUID, amount: Decimal, reason: str) -> RefundORM:
        ref = RefundORM(payment_id=payment_id, amount=amount, reason=reason)
        self._session.add(ref)
        await self._session.commit()
        await self._session.refresh(ref)
        return ref
