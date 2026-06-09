from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from src.application.services import ReportingService
from src.presentation.dependencies import require_staff, require_reports
from src.presentation.schemas import IncomeReportResponse, AppointmentStatsResponse, DemandReportResponse

router = APIRouter()


@router.get("/reports/income", response_model=IncomeReportResponse)
async def income_report(
    doctor_id: Optional[UUID] = None,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    group_by: Optional[str] = Query(None, pattern="^(doctor|period|specialty)?$"),
    current_user: dict = Depends(require_staff),
):
    service = ReportingService(current_user["token"])
    return await service.income_report(doctor_id, start_date, end_date, group_by)


@router.get("/reports/appointments", response_model=AppointmentStatsResponse)
async def appointment_stats(
    current_user: dict = Depends(require_reports),
):
    service = ReportingService(current_user["token"])
    return await service.appointment_stats()


@router.get("/reports/demand", response_model=DemandReportResponse)
async def demand_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_staff),
):
    service = ReportingService(current_user["token"])
    return await service.demand_report(start_date, end_date)


@router.get("/reports/export")
async def export_report(
    report_type: str,
    format: str = Query("csv", alias="format"),
    doctor_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(require_staff),
):
    service = ReportingService(current_user["token"])
    fmt = format.lower()

    if fmt == "csv":
        csv_data = await service.export_csv(report_type, doctor_id, start_date, end_date)
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.csv"},
        )
    if fmt == "pdf":
        pdf_data = await service.export_pdf(report_type, doctor_id, start_date, end_date)
        return StreamingResponse(
            iter([pdf_data]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.pdf"},
        )
    if fmt in ("xlsx", "excel"):
        xlsx_data = await service.export_xlsx(report_type, doctor_id, start_date, end_date)
        return StreamingResponse(
            iter([xlsx_data]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.xlsx"},
        )
    raise HTTPException(400, "Supported formats: csv, pdf, xlsx")
