from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.services import ReportingService


def _reporting_service() -> ReportingService:
    return ReportingService("test-token")


async def test_income_report_filters_by_doctor():
    doctor_a = uuid4()
    doctor_b = uuid4()
    invoices = [
        {"doctor_id": str(doctor_a), "amount": 100, "created_at": "2025-01-01"},
        {"doctor_id": str(doctor_b), "amount": 200, "created_at": "2025-01-02"},
    ]
    service = _reporting_service()
    service._fetch_billing_invoices = AsyncMock(return_value=invoices)

    result = await service.income_report(doctor_id=doctor_a)

    assert result["count"] == 1
    assert result["total_income"] == 100.0
    assert result["invoices"][0]["doctor_id"] == str(doctor_a)


async def test_appointment_stats_groups_by_status():
    appointments = [
        {"status": "programada"},
        {"status": "programada"},
        {"status": "completada"},
    ]
    service = _reporting_service()
    service._fetch_scheduling_appointments = AsyncMock(return_value=appointments)

    result = await service.appointment_stats()

    assert result["total"] == 3
    assert result["by_status"]["programada"] == 2
    assert result["by_status"]["completada"] == 1
