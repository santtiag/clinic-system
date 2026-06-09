import httpx
from datetime import datetime

class AdminDashboardService:
    def __init__(self, token: str):
        self._token = token
        self._headers = {"Authorization": f"Bearer {token}"}
        self._client = httpx.AsyncClient(timeout=10.0)

    async def _get(self, url: str, params=None):
        resp = await self._client.get(url, headers=self._headers, params=params or {})
        resp.raise_for_status()
        return resp.json()

    async def dashboard_summary(self):
        try:
            users = await self._get("http://identity-service:8000/auth/users")
            total_users = len(users)
            total_patients = len([u for u in users if u.get("role") == "patient"])
            total_doctors = len([u for u in users if u.get("role") == "doctor"])
            pending_doctors = len([u for u in users if u.get("role") == "doctor" and not u.get("isActive")])
        except Exception:
            total_users = total_patients = total_doctors = pending_doctors = None

        try:
            appointments = await self._get("http://scheduling-service:8000/appointments/all")
            total_appointments = len(appointments)
            today_str = str(datetime.now().date())
            completed_today = len([
                a for a in appointments
                if a.get("status") == "completada" and a.get("created_at", "").startswith(today_str)
            ])
        except Exception:
            total_appointments = completed_today = None

        try:
            pending = await self._get("http://billing-service:8000/invoices/pending")
            pending_count = len(pending)
            pending_amount = sum(float(i.get("amount", 0)) for i in pending)
        except Exception:
            pending_count = pending_amount = None

        try:
            income = await self._get("http://reporting-service:8000/reports/income")
            total_income = income.get("total_income")
        except Exception:
            total_income = None

        return {
            "users": {
                "total": total_users,
                "patients": total_patients,
                "doctors": total_doctors,
                "pending_doctors": pending_doctors,
            },
            "appointments": {
                "total": total_appointments,
                "completed_today": completed_today,
            },
            "billing": {
                "pending_invoices": pending_count,
                "pending_amount": pending_amount,
                "total_income": total_income,
            },
            "generated_at": datetime.now().isoformat(),
        }

    async def get_audit_logs(self, user_id=None, start=None, end=None):
        params = {}
        if user_id:
            params["user_id"] = user_id
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self._get("http://identity-service:8000/auth/audit", params)
