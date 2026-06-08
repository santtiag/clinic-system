from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class IncomeReportResponse(BaseModel):
    total_income: float
    count: int
    invoices: List[Dict[str, Any]]

class AppointmentStatsResponse(BaseModel):
    total: int
    by_status: Dict[str, int]
