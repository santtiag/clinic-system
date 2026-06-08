from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.application.services import ReportingService
from src.presentation.dependencies import get_current_user
from src.presentation.schemas import IncomeReportResponse, AppointmentStatsResponse

router = APIRouter()

@router.get("/reports/income", response_model=IncomeReportResponse)
async def income_report(
    doctor_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "staff"):
        raise HTTPException(403, "Not authorized")
    service = ReportingService(current_user["token"])
    return await service.income_report(doctor_id, start_date, end_date)

@router.get("/reports/appointments", response_model=AppointmentStatsResponse)
async def appointment_stats(
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "staff", "doctor"):
        raise HTTPException(403, "Not authorized")
    service = ReportingService(current_user["token"])
    return await service.appointment_stats()

@router.get("/reports/export")
async def export_report(
    report_type: str,
    format: str = "csv",
    doctor_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "staff"):
        raise HTTPException(403, "Not authorized")
    if format != "csv":
        raise HTTPException(400, "Only CSV export is supported in this iteration")
    service = ReportingService(current_user["token"])
    csv_data = await service.export_csv(report_type, doctor_id, start_date, end_date)
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report_type}_report.csv"}
    )
