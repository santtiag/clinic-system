from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User, Role
from src.infrastructure.repositories import SQLUserRepository
from src.infrastructure.security import hash_password, verify_password, create_access_token
from src.presentation.schemas import PatientRegister, LoginRequest


class AuthService:
    def __init__(self, session: AsyncSession):
        self._repo = SQLUserRepository(session)

    async def register_patient(self, payload: PatientRegister) -> dict:
        if await self._repo.get_by_username(payload.username):
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
        if await self._repo.get_by_email(str(payload.email)):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already exists")
        if await self._repo.get_by_dni(payload.dni):
            raise HTTPException(status.HTTP_409_CONFLICT, "DNI already exists")

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
        await self._repo.create(user, hashed)
        return {"message": "Patient registered successfully", "username": user.username}

    async def authenticate(self, payload: LoginRequest) -> str:
        db_user = await self._repo.get_by_username(payload.username)
        if not db_user or not verify_password(payload.password, db_user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        return create_access_token(
            {"sub": str(db_user.id), "role": db_user.role}
        )

    async def list_users(self):
        return await self._repo.list_all()
