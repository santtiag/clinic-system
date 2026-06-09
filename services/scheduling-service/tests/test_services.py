from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.application.services import SchedulingService
from src.domain.models import AppointmentStatus


@pytest.fixture
def scheduling_service():
    session = MagicMock()
    service = SchedulingService(session)
    service._doctors = AsyncMock()
    service._slots = AsyncMock()
    service._appointments = AsyncMock()
    service._history = AsyncMock()
    return service


async def test_book_appointment_slot_unavailable(scheduling_service):
    slot_id = uuid4()
    patient_id = uuid4()
    scheduling_service._slots.get_by_id = AsyncMock(
        return_value=SimpleNamespace(id=slot_id, doctor_id=uuid4(), is_available=False)
    )

    with pytest.raises(HTTPException) as exc:
        await scheduling_service.book_appointment(patient_id, slot_id, "Consulta general")

    assert exc.value.status_code == 409


async def test_update_appointment_status_forbidden_for_patient(scheduling_service):
    with pytest.raises(HTTPException) as exc:
        await scheduling_service.update_appointment_status(uuid4(), "confirmada", "patient")

    assert exc.value.status_code == 403


@patch("src.application.services.publish_event", new_callable=AsyncMock)
async def test_fsm_rejects_invalid_transition(mock_publish, scheduling_service):
    appt_id = uuid4()
    scheduling_service._appointments.get_by_id = AsyncMock(
        return_value=SimpleNamespace(
            id=appt_id,
            patient_id=uuid4(),
            doctor_id=uuid4(),
            status=AppointmentStatus.SCHEDULED,
        )
    )

    with pytest.raises(HTTPException) as exc:
        await scheduling_service.update_appointment_status(
            appt_id, "completada", "doctor", uuid4()
        )

    assert exc.value.status_code == 409
    assert "Invalid transition" in exc.value.detail


async def test_cancel_within_24h_rejected(scheduling_service):
    appt_id = uuid4()
    patient_id = uuid4()
    slot_id = uuid4()
    scheduling_service._appointments.get_by_id = AsyncMock(
        return_value=SimpleNamespace(
            id=appt_id,
            patient_id=patient_id,
            slot_id=slot_id,
            status=AppointmentStatus.SCHEDULED,
        )
    )
    scheduling_service._slots.get_by_id = AsyncMock(
        return_value=SimpleNamespace(
            start_time=datetime.now() + timedelta(hours=2),
        )
    )

    with pytest.raises(HTTPException) as exc:
        await scheduling_service.cancel_appointment(appt_id, patient_id, "patient")

    assert exc.value.status_code == 409
    assert "24 hours" in exc.value.detail
