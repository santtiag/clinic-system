from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.application.services import BillingService
from src.domain.models import InvoiceStatus


@pytest.fixture
def billing_service():
    session = MagicMock()
    service = BillingService(session)
    service._invoices = AsyncMock()
    service._payments = AsyncMock()
    service._refunds = AsyncMock()
    return service


async def test_process_payment_invoice_not_found(billing_service):
    invoice_id = uuid4()
    billing_service._invoices.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc:
        await billing_service.process_payment(invoice_id, 50.0, "efectivo")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Invoice not found"
    billing_service._payments.create.assert_not_awaited()


async def test_process_payment_marks_invoice_paid_when_full_amount(billing_service):
    invoice_id = uuid4()
    invoice = SimpleNamespace(
        id=invoice_id,
        amount=Decimal("50.00"),
        status=InvoiceStatus.PENDING,
    )
    billing_service._invoices.get_by_id = AsyncMock(return_value=invoice)
    billing_service._payments.create = AsyncMock(
        return_value=SimpleNamespace(id=uuid4())
    )
    billing_service._invoices.update_status = AsyncMock()

    await billing_service.process_payment(invoice_id, 50.0, "efectivo")

    billing_service._payments.create.assert_awaited_once()
    billing_service._invoices.update_status.assert_awaited_once_with(
        invoice_id,
        InvoiceStatus.PAID,
    )
