from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import UserORM
from src.domain.models import User


class SQLUserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_username(self, username: str) -> Optional[UserORM]:
        result = await self._session.execute(
            select(UserORM).where(UserORM.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserORM]:
        result = await self._session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_dni(self, dni: str) -> Optional[UserORM]:
        result = await self._session.execute(
            select(UserORM).where(UserORM.dni == dni)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User, hashed_password: str) -> UserORM:
        db_user = UserORM(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role,
            dni=user.dni,
            first_name=user.first_name,
            last_name=user.last_name,
            date_of_birth=user.date_of_birth,
        )
        self._session.add(db_user)
        await self._session.commit()
        await self._session.refresh(db_user)
        return db_user

    async def list_all(self):
        from sqlalchemy import select
        from src.infrastructure.models import UserORM  # ajusta el import según tu estructura
        result = await self._session.execute(select(UserORM))
        return result.scalars().all()
