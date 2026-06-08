from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from src.application.services import AuthService
from src.infrastructure.security import hash_password, verify_password
from src.presentation.schemas import PatientRegister


@pytest.fixture
def auth_service():
    session = MagicMock()
    service = AuthService(session)
    service._repo = AsyncMock()
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


async def test_register_patient_conflict_username(auth_service):
    auth_service._repo.get_by_username = AsyncMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc:
        await auth_service.register_patient(_patient_payload())

    assert exc.value.status_code == 409
    assert exc.value.detail == "Username already exists"
    auth_service._repo.create.assert_not_awaited()


def test_hash_and_verify_password():
    hashed = hash_password("securepass123")

    assert verify_password("securepass123", hashed)
    assert not verify_password("wrongpassword", hashed)
