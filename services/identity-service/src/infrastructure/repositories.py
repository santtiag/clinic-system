from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import UserORM, AuditLogORM
from src.domain.models import User, Role


class SQLUserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[UserORM]:
        result = await self._session.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        return result.scalar_one_or_none()

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
            specialty=user.specialty,
            license_number=user.license_number,
            is_active=user.is_active,
        )
        self._session.add(db_user)
        await self._session.commit()
        await self._session.refresh(db_user)
        return db_user

    async def list_all(self) -> List[UserORM]:
        result = await self._session.execute(select(UserORM))
        return result.scalars().all()

    async def update(self, user_id: UUID, **fields) -> Optional[UserORM]:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        for key, value in fields.items():
            if hasattr(db_user, key) and value is not None:
                setattr(db_user, key, value)
        await self._session.commit()
        await self._session.refresh(db_user)
        return db_user

    async def delete(self, user_id: UUID) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False
        await self._session.delete(db_user)
        await self._session.commit()
        return True


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_logs(
        self,
        user_id: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> List[AuditLogORM]:
        query = select(AuditLogORM).order_by(AuditLogORM.occurred_at.desc())
        conditions = []
        if user_id:
            conditions.append(AuditLogORM.payload.contains(user_id))
        if start:
            conditions.append(AuditLogORM.occurred_at >= start)
        if end:
            conditions.append(AuditLogORM.occurred_at <= end)
        if conditions:
            query = query.where(and_(*conditions))
        result = await self._session.execute(query.limit(200))
        return result.scalars().all()
