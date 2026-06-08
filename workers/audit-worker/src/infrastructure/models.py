import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database import Base

class AuditLogORM(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    routing_key = Column(String(255), nullable=False)
    payload = Column(Text, nullable=False)
    occurred_at = Column(DateTime, default=datetime.now(), nullable=False)
