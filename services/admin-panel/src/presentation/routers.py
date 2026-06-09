from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.application.services import AdminDashboardService
from src.presentation.dependencies import require_admin

router = APIRouter()

@router.get("/admin/dashboard")
async def dashboard(admin=Depends(require_admin)):
    service = AdminDashboardService(admin["token"])
    return await service.dashboard_summary()

@router.get("/admin/audit")
async def audit_logs(
    user_id: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    admin=Depends(require_admin),
):
    service = AdminDashboardService(admin["token"])
    return await service.get_audit_logs(user_id, start, end)

@router.get("/admin/health")
async def admin_health():
    return {"status": "ok", "service": "admin-panel"}
