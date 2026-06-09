from datetime import datetime
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.presentation.schemas import (
    PatientRegister, DoctorRegister, LoginRequest, TokenResponse, UserUpdate,
    StaffCreate,
)
from src.application.services import AuthService
from src.presentation.dependencies import get_db, get_current_user, require_admin

auth_router = APIRouter()


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


@auth_router.post("/register/patient", status_code=status.HTTP_201_CREATED)
async def register_patient(
    payload: PatientRegister, db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    return await service.register_patient(payload)


@auth_router.post("/register/doctor", status_code=status.HTTP_201_CREATED)
async def register_doctor(
    payload: DoctorRegister, db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    return await service.register_doctor(payload)


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    token = await service.authenticate(payload)
    return TokenResponse(access_token=token)


@auth_router.get("/me")
async def me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.get_user(UUID(current_user.get("user_id")))
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    full_name = " ".join(
        part for part in [user.first_name, user.last_name] if part
    ).strip()
    return {
        "user_id": str(user.id),
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "username": user.username,
        "name": full_name or user.username,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "email": user.email,
        "specialty": user.specialty,
    }


@auth_router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    service = AuthService(db)
    users = await service.list_users()
    return [
        {
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
        for u in users
    ]


@auth_router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_staff(
    payload: StaffCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    service = AuthService(db)
    return await service.create_staff(payload)


@auth_router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    service = AuthService(db)
    return await service.activate_user(user_id)


@auth_router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    service = AuthService(db)
    return await service.update_user(user_id, payload)


@auth_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    service = AuthService(db)
    await service.delete_user(user_id)


@auth_router.get("/audit")
async def audit_logs(
    user_id: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
):
    service = AuthService(db)
    return await service.get_audit_logs(user_id, _parse_date(start), _parse_date(end))
