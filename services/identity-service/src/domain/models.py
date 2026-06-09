from datetime import date
from enum import Enum


class Role(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    STAFF = "staff"


class User:
    """Entidad de dominio pura. No depende de SQLAlchemy ni de FastAPI."""
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        hashed_password: str,
        role: Role,
        dni: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        specialty: str | None = None,
        license_number: str | None = None,
        is_active: bool = True,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.role = role
        self.dni = dni
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.specialty = specialty
        self.license_number = license_number
        self.is_active = is_active
