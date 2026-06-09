from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User, Role
from src.infrastructure.repositories import SQLUserRepository, AuditRepository
from src.infrastructure.security import hash_password, verify_password, create_access_token
from src.infrastructure.messaging import publish_event
from src.presentation.schemas import (
    PatientRegister, DoctorRegister, LoginRequest, UserUpdate, StaffCreate,
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self._repo = SQLUserRepository(session)
        self._audit = AuditRepository(session)

    def _serialize_user(self, u) -> dict:
        return {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "dni": u.dni,
            "firstName": u.first_name,
            "lastName": u.last_name,
            "specialty": u.specialty,
            "licenseNumber": u.license_number,
            "isActive": u.is_active,
        }

    async def _ensure_unique(self, payload) -> None:
        if await self._repo.get_by_username(payload.username):
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
        if await self._repo.get_by_email(str(payload.email)):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")
        if await self._repo.get_by_dni(payload.dni):
            raise HTTPException(status.HTTP_409_CONFLICT, "DNI already exists")

    async def register_patient(self, payload: PatientRegister) -> dict:
        await self._ensure_unique(payload)
        user = User(
            user_id="",
            username=payload.username,
            email=str(payload.email),
            hashed_password="",
            role=Role.PATIENT,
            dni=payload.dni,
            first_name=payload.first_name,
            last_name=payload.last_name,
            date_of_birth=payload.date_of_birth,
        )
        hashed = hash_password(payload.password)
        db_user = await self._repo.create(user, hashed)
        return {"message": "Patient registered successfully", "username": db_user.username}

    async def register_doctor(self, payload: DoctorRegister) -> dict:
        await self._ensure_unique(payload)
        user = User(
            user_id="",
            username=payload.username,
            email=str(payload.email),
            hashed_password="",
            role=Role.DOCTOR,
            dni=payload.dni,
            first_name=payload.first_name,
            last_name=payload.last_name,
            date_of_birth=payload.date_of_birth,
            specialty=payload.specialty,
            license_number=payload.license_number,
            is_active=False,
        )
        hashed = hash_password(payload.password)
        db_user = await self._repo.create(user, hashed)
        publish_event("doctor.registered", {
            "user_id": str(db_user.id),
            "username": db_user.username,
            "full_name": " ".join(
                part for part in [db_user.first_name, db_user.last_name] if part
            ).strip() or db_user.username,
            "specialty": db_user.specialty,
            "license_number": db_user.license_number,
        })
        return {
            "message": "Doctor registered. Pending admin validation.",
            "username": db_user.username,
        }

    async def create_staff(self, payload: StaffCreate) -> dict:
        await self._ensure_unique(payload)
        role = Role(payload.role)
        if role == Role.DOCTOR and not payload.specialty:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "specialty is required when creating a doctor",
            )
        user = User(
            user_id="",
            username=payload.username,
            email=str(payload.email),
            hashed_password="",
            role=role,
            dni=payload.dni,
            first_name=payload.first_name,
            last_name=payload.last_name,
            date_of_birth=payload.date_of_birth,
            specialty=payload.specialty,
            license_number=payload.license_number,
            is_active=True,
        )
        hashed = hash_password(payload.password)
        db_user = await self._repo.create(user, hashed)
        if role == Role.DOCTOR:
            publish_event("doctor.registered", {
                "user_id": str(db_user.id),
                "username": db_user.username,
                "full_name": " ".join(
                    part for part in [db_user.first_name, db_user.last_name] if part
                ).strip() or db_user.username,
                "specialty": db_user.specialty,
                "license_number": db_user.license_number,
            })
        publish_event("users.created", {
            "user_id": str(db_user.id),
            "role": role.value,
        })
        return self._serialize_user(db_user)

    async def authenticate(self, payload: LoginRequest) -> str:
        db_user = await self._repo.get_by_username(payload.username)
        if not db_user or not verify_password(payload.password, db_user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        if not db_user.is_active:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Account pending validation or deactivated",
            )
        role = db_user.role.value if hasattr(db_user.role, "value") else str(db_user.role)
        full_name = " ".join(
            part for part in [db_user.first_name, db_user.last_name] if part
        ).strip()
        return create_access_token({
            "sub": str(db_user.id),
            "role": role,
            "name": full_name or db_user.username,
            "username": db_user.username,
        })

    async def list_users(self):
        return await self._repo.list_all()

    async def get_user(self, user_id: UUID):
        return await self._repo.get_by_id(user_id)

    async def activate_user(self, user_id: UUID) -> dict:
        user = await self._repo.update(user_id, is_active=True)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        publish_event("users.activated", {"user_id": str(user_id), "role": user.role.value})
        return self._serialize_user(user)

    async def update_user(self, user_id: UUID, payload: UserUpdate) -> dict:
        fields = {}
        if payload.role is not None:
            fields["role"] = Role(payload.role)
        if payload.is_active is not None:
            fields["is_active"] = payload.is_active
        if payload.specialty is not None:
            fields["specialty"] = payload.specialty
        user = await self._repo.update(user_id, **fields)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        publish_event("users.updated", {"user_id": str(user_id), "changes": fields})
        return self._serialize_user(user)

    async def delete_user(self, user_id: UUID) -> dict:
        deleted = await self._repo.delete(user_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        publish_event("users.deleted", {"user_id": str(user_id)})
        return {"message": "User deleted"}

    async def get_audit_logs(self, user_id: str | None, start, end):
        logs = await self._audit.list_logs(user_id, start, end)
        return [
            {
                "id": str(log.id),
                "eventType": log.event_type,
                "routingKey": log.routing_key,
                "payload": log.payload,
                "occurredAt": log.occurred_at.isoformat(),
            }
            for log in logs
        ]
