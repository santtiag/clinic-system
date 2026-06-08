import io
import csv
from typing import Optional
from uuid import UUID
import httpx

class ReportingService:
    def __init__(self, token: str):
        self._token = token
        self._headers = {"Authorization": f"Bearer {token}"}
        self._client = httpx.AsyncClient(timeout=10.0)

    async def _fetch_billing_invoices(self, status: Optional[str] = None):
        url = "http://billing-service:8000/invoices"
        params = {"status": status} if status else {}
        resp = await self._client.get(url, headers=self._headers, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _fetch_scheduling_appointments(self):
        url = "http://scheduling-service:8000/appointments/all"
        resp = await self._client.get(url, headers=self._headers)
        resp.raise_for_status()
        return resp.json()

    async def income_report(self, doctor_id: Optional[UUID] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None):
        invoices = await self._fetch_billing_invoices(status="pagado")
        filtered = invoices
        if doctor_id:
            filtered = [i for i in filtered if str(i.get("doctor_id")) == str(doctor_id)]
        if start_date or end_date:
            filtered = [
                i for i in filtered
                if (not start_date or i.get("created_at", "").startswith(start_date))
                and (not end_date or i.get("created_at", "").startswith(end_date))
            ]
        total = sum(float(i.get("amount", 0)) for i in filtered)
        return {"total_income": round(total, 2), "count": len(filtered), "invoices": filtered}

    async def appointment_stats(self):
        appointments = await self._fetch_scheduling_appointments()
        from collections import Counter
        statuses = Counter(a.get("status") for a in appointments)
        return {"total": len(appointments), "by_status": dict(statuses)}

    async def export_csv(self, report_type: str, doctor_id: Optional[UUID] = None,
                         start_date: Optional[str] = None, end_date: Optional[str] = None):
        if report_type == "income":
            data = await self.income_report(doctor_id, start_date, end_date)
            invoices = data["invoices"]
            output = io.StringIO()
            if invoices:
                writer = csv.DictWriter(output, fieldnames=list(invoices[0].keys()))
                writer.writeheader()
                for row in invoices:
                    writer.writerow({k: str(v) for k, v in row.items()})
            else:
                output.write("No data\n")
            return output.getvalue()
        elif report_type == "appointments":
            data = await self.appointment_stats()
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["status", "count"])
            for status, count in data["by_status"].items():
                writer.writerow([status, count])
            writer.writerow(["total", data["total"]])
            return output.getvalue()
        else:
            raise ValueError("Unknown report type")
