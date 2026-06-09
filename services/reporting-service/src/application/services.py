import io
import csv
from collections import Counter, defaultdict
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

    def _filter_by_date(self, items, start_date, end_date, date_field="created_at"):
        if not start_date and not end_date:
            return items
        return [
            i for i in items
            if (not start_date or i.get(date_field, "").startswith(start_date))
            and (not end_date or i.get(date_field, "").startswith(end_date))
        ]

    async def income_report(
        self,
        doctor_id: Optional[UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_by: Optional[str] = None,
    ):
        invoices = await self._fetch_billing_invoices(status="pagado")
        filtered = invoices
        if doctor_id:
            filtered = [i for i in filtered if str(i.get("doctor_id")) == str(doctor_id)]
        filtered = self._filter_by_date(filtered, start_date, end_date)
        total = sum(float(i.get("amount", 0)) for i in filtered)

        grouped = None
        if group_by == "doctor":
            by_doctor = defaultdict(float)
            for inv in filtered:
                by_doctor[str(inv.get("doctor_id"))] += float(inv.get("amount", 0))
            grouped = {"by_doctor": dict(by_doctor)}
        elif group_by == "period":
            by_period = defaultdict(float)
            for inv in filtered:
                period = str(inv.get("created_at", ""))[:7]
                by_period[period] += float(inv.get("amount", 0))
            grouped = {"by_period": dict(by_period)}

        return {
            "total_income": round(total, 2),
            "count": len(filtered),
            "invoices": filtered,
            "grouped": grouped,
        }

    async def appointment_stats(self):
        appointments = await self._fetch_scheduling_appointments()
        statuses = Counter(a.get("status") for a in appointments)
        return {"total": len(appointments), "by_status": dict(statuses)}

    async def demand_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        appointments = await self._fetch_scheduling_appointments()
        filtered = self._filter_by_date(appointments, start_date, end_date)
        specialty_counter = Counter()
        diagnosis_counter = Counter()
        for appt in filtered:
            reason = appt.get("reason") or "Consulta general"
            specialty_counter[reason.split(" - ")[0] if " - " in reason else "Medicina General"] += 1
            if "CIE" in reason.upper() or "diagn" in reason.lower():
                diagnosis_counter[reason] += 1
            else:
                diagnosis_counter["Consulta general (Z00)"] += 1

        top_specialties = [
            {"specialty": k, "count": v}
            for k, v in specialty_counter.most_common(10)
        ]
        top_diagnoses = [
            {"diagnosis": k, "count": v, "percentage": round(v / max(len(filtered), 1) * 100, 1)}
            for k, v in diagnosis_counter.most_common(10)
        ]
        return {
            "top_specialties": top_specialties,
            "top_diagnoses": top_diagnoses,
            "total_appointments": len(filtered),
        }

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
        elif report_type == "demand":
            data = await self.demand_report(start_date, end_date)
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["type", "name", "count"])
            for item in data["top_specialties"]:
                writer.writerow(["specialty", item["specialty"], item["count"]])
            for item in data["top_diagnoses"]:
                writer.writerow(["diagnosis", item["diagnosis"], item["count"]])
            return output.getvalue()
        raise ValueError("Unknown report type")

    async def export_pdf(self, report_type: str, doctor_id: Optional[UUID] = None,
                         start_date: Optional[str] = None, end_date: Optional[str] = None) -> bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            csv_data = await self.export_csv(report_type, doctor_id, start_date, end_date)
            return csv_data.encode("utf-8")

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(72, 750, f"Reporte: {report_type}")
        pdf.setFont("Helvetica", 10)
        y = 720
        if report_type == "income":
            data = await self.income_report(doctor_id, start_date, end_date)
            lines = [
                f"Ingresos totales: ${data['total_income']}",
                f"Facturas: {data['count']}",
            ]
        elif report_type == "demand":
            data = await self.demand_report(start_date, end_date)
            lines = [f"Citas totales: {data['total_appointments']}"]
            for item in data["top_specialties"][:5]:
                lines.append(f"  {item['specialty']}: {item['count']}")
        else:
            data = await self.appointment_stats()
            lines = [f"Total citas: {data['total']}"]
            for status, count in data["by_status"].items():
                lines.append(f"  {status}: {count}")

        for line in lines:
            pdf.drawString(72, y, line)
            y -= 16
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer.read()

    async def export_xlsx(self, report_type: str, doctor_id: Optional[UUID] = None,
                          start_date: Optional[str] = None, end_date: Optional[str] = None) -> bytes:
        try:
            from openpyxl import Workbook
        except ImportError:
            return (await self.export_csv(report_type, doctor_id, start_date, end_date)).encode("utf-8")

        wb = Workbook()
        ws = wb.active
        ws.title = report_type

        if report_type == "income":
            data = await self.income_report(doctor_id, start_date, end_date)
            invoices = data["invoices"]
            if invoices:
                headers = list(invoices[0].keys())
                ws.append(headers)
                for row in invoices:
                    ws.append([str(row.get(h, "")) for h in headers])
            else:
                ws.append(["No data"])
        elif report_type == "demand":
            data = await self.demand_report(start_date, end_date)
            ws.append(["Especialidad", "Consultas"])
            for item in data["top_specialties"]:
                ws.append([item["specialty"], item["count"]])
        else:
            data = await self.appointment_stats()
            ws.append(["Estado", "Cantidad"])
            for status, count in data["by_status"].items():
                ws.append([status, count])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.read()
