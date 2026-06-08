from src.application.services import AdminDashboardService


def _admin_service() -> AdminDashboardService:
    return AdminDashboardService("test-token")


async def test_dashboard_summary_aggregates_users():
    users = [
        {"role": "patient"},
        {"role": "patient"},
        {"role": "doctor"},
        {"role": "admin"},
    ]
    service = _admin_service()

    async def mock_get(url: str):
        if "identity-service" in url:
            return users
        if "scheduling-service" in url:
            return []
        if "billing-service" in url and "pending" in url:
            return []
        if "reporting-service" in url:
            return {"total_income": 0}
        return []

    service._get = mock_get

    result = await service.dashboard_summary()

    assert result["users"]["total"] == 4
    assert result["users"]["patients"] == 2
    assert result["users"]["doctors"] == 1


async def test_dashboard_summary_handles_service_errors():
    service = _admin_service()

    async def mock_get(url: str):
        if "identity-service" in url:
            raise RuntimeError("identity unavailable")
        if "scheduling-service" in url:
            return [{"status": "completada", "created_at": "2025-01-01"}]
        if "billing-service" in url and "pending" in url:
            raise RuntimeError("billing unavailable")
        if "reporting-service" in url:
            return {"total_income": 500}
        return []

    service._get = mock_get

    result = await service.dashboard_summary()

    assert result["users"]["total"] is None
    assert result["appointments"]["total"] == 1
    assert result["billing"]["pending_invoices"] is None
    assert result["billing"]["total_income"] == 500
