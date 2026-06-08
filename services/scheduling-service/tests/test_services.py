from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.application.services import SchedulingService


@pytest.fixture
def scheduling_service():
    session = MagicMock()
    service = SchedulingService(session)
    service._doctors = AsyncMock()
    service._slots = AsyncMock()
    service._appointments = AsyncMock()
    return service


async def test_book_appointment_slot_unavailable(scheduling_service):
    slot_id = uuid4()
    patient_id = uuid4()
    scheduling_service._slots.get_by_id = AsyncMock(
        return_value=SimpleNamespace(
            id=slot_id,
            doctor_id=uuid4(),
            is_available=False,
        )
    )

    with pytest.raises(HTTPException) as exc:
        await scheduling_service.book_appointment(patient_id, slot_id, "Consulta general")

    assert exc.value.status_code == 409
    assert exc.value.detail == "Slot not available"
    scheduling_service._slots.mark_booked.assert_not_awaited()


async def test_update_appointment_status_forbidden_for_patient(scheduling_service):
    with pytest.raises(HTTPException) as exc:
        await scheduling_service.update_appointment_status(
            uuid4(),
            "confirmada",
            "patient",
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Only medical staff can update status"
    scheduling_service._appointments.get_by_id.assert_not_awaited()
