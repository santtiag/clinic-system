from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.models import AuditLogORM

class AuditRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event_type: str, routing_key: str, payload: str):
        log = AuditLogORM(
            event_type=event_type,
            routing_key=routing_key,
            payload=payload,
        )
        self._session.add(log)
        await self._session.commit()
