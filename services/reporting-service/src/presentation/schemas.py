from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class IncomeReportResponse(BaseModel):
    total_income: float
    count: int
    invoices: List[Dict[str, Any]]
    grouped: Optional[Dict[str, Any]] = None

class AppointmentStatsResponse(BaseModel):
    total: int
    by_status: Dict[str, int]

class DemandReportResponse(BaseModel):
    top_specialties: List[Dict[str, Any]]
    top_diagnoses: List[Dict[str, Any]]
    total_appointments: int
