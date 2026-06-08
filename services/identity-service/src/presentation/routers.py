from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.presentation.schemas import PatientRegister, LoginRequest, TokenResponse
from src.application.services import AuthService
from src.presentation.dependencies import get_db, get_current_user

auth_router = APIRouter()


@auth_router.post("/register/patient", status_code=status.HTTP_201_CREATED)
async def register_patient(
    payload: PatientRegister, db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    return await service.register_patient(payload)


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    token = await service.authenticate(payload)
    return TokenResponse(access_token=token)


@auth_router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user.get("sub"), "role": current_user.get("role")}

@auth_router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    service = AuthService(db)
    users = await service.list_users()
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "dni": u.dni,
            "first_name": u.first_name,
            "last_name": u.last_name,
        }
        for u in users
    ]
