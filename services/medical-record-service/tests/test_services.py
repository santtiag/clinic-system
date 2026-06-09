from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.services import MedicalRecordService


@pytest.fixture
def medical_record_service():
    session = MagicMock()
    service = MedicalRecordService(session)
    service._records = AsyncMock()
    service._evolutions = AsyncMock()
    service._prescriptions = AsyncMock()
    service._attachments = AsyncMock()
    return service


async def test_add_evolution_creates_note_for_existing_record(medical_record_service):
    patient_id = uuid4()
    doctor_id = uuid4()
    record_id = uuid4()
    record = SimpleNamespace(id=record_id)
    note = SimpleNamespace(id=uuid4(), observations="Paciente estable")

    medical_record_service._records.get_or_create_by_patient = AsyncMock(return_value=record)
    medical_record_service._evolutions.create = AsyncMock(return_value=note)

    result = await medical_record_service.add_evolution(
        patient_id,
        doctor_id,
        "Paciente estable",
    )

    medical_record_service._records.get_or_create_by_patient.assert_awaited_once_with(patient_id)
    medical_record_service._evolutions.create.assert_awaited_once_with(
        record_id,
        doctor_id,
        "Paciente estable",
    )
    assert result == note


async def test_get_patient_history_returns_record_and_evolutions(medical_record_service):
    patient_id = uuid4()
    record_id = uuid4()
    record = SimpleNamespace(id=record_id)
    evolutions = [SimpleNamespace(id=uuid4()), SimpleNamespace(id=uuid4())]

    medical_record_service._records.get_or_create_by_patient = AsyncMock(return_value=record)
    medical_record_service._evolutions.list_by_patient = AsyncMock(return_value=evolutions)
    medical_record_service._prescriptions.list_by_patient = AsyncMock(return_value=[])
    medical_record_service._attachments.list_by_evolution = AsyncMock(return_value=[])

    result = await medical_record_service.get_patient_history(patient_id)

    assert result["record_id"] == record_id
    assert result["patient_id"] == patient_id
    assert result["evolutions"] == evolutions
    assert result["prescriptions"] == []
