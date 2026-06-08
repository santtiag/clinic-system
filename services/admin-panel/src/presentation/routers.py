from fastapi import APIRouter, Depends
from src.application.services import AdminDashboardService
from src.presentation.dependencies import require_admin

router = APIRouter()

@router.get("/admin/dashboard")
async def dashboard(admin=Depends(require_admin)):
    service = AdminDashboardService(admin["token"])
    return await service.dashboard_summary()

@router.get("/admin/health")
async def admin_health():
    return {"status": "ok", "service": "admin-panel"}
