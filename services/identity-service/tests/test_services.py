from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.application.services import AuthService
from src.domain.models import Role
from src.infrastructure.security import hash_password, verify_password
from src.presentation.schemas import PatientRegister, DoctorRegister, LoginRequest


@pytest.fixture
def auth_service():
    session = MagicMock()
    service = AuthService(session)
    service._repo = AsyncMock()
    service._audit = AsyncMock()
    return service


def _patient_payload() -> PatientRegister:
    return PatientRegister(
        username="juan_perez",
        email="juan@example.com",
        password="password123",
        dni="12345678",
        first_name="Juan",
        last_name="Perez",
        date_of_birth=date(1990, 1, 1),
    )


def _doctor_payload() -> DoctorRegister:
    return DoctorRegister(
        username="dr_garcia",
        email="garcia@example.com",
        password="password123",
        dni="87654321",
        first_name="Ana",
        last_name="Garcia",
        date_of_birth=date(1985, 5, 15),
        specialty="Medicina General",
        license_number="COL-12345",
    )


async def test_register_patient_conflict_username(auth_service):
    auth_service._repo.get_by_username = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await auth_service.register_patient(_patient_payload())

    assert exc.value.status_code == 409
    auth_service._repo.create.assert_not_awaited()


@patch("src.application.services.publish_event")
async def test_register_doctor_pending_validation(mock_publish, auth_service):
    auth_service._repo.get_by_username = AsyncMock(return_value=None)
    auth_service._repo.get_by_email = AsyncMock(return_value=None)
    auth_service._repo.get_by_dni = AsyncMock(return_value=None)
    auth_service._repo.create = AsyncMock(return_value=MagicMock(username="dr_garcia", id="uuid"))

    result = await auth_service.register_doctor(_doctor_payload())

    assert "Pending admin validation" in result["message"]
    mock_publish.assert_called_once()


async def test_authenticate_inactive_user(auth_service):
    inactive = MagicMock()
    inactive.hashed_password = hash_password("password123")
    inactive.is_active = False
    auth_service._repo.get_by_username = AsyncMock(return_value=inactive)

    with pytest.raises(HTTPException) as exc:
        await auth_service.authenticate(LoginRequest(username="dr", password="password123"))

    assert exc.value.status_code == 403


def test_hash_and_verify_password():
    hashed = hash_password("securepass123")
    assert verify_password("securepass123", hashed)
    assert not verify_password("wrongpassword", hashed)
