import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Boolean, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database import Base
from src.domain.models import Role


class UserORM(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(Role, name="role_enum"), nullable=False, default=Role.PATIENT)
    dni = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    specialty = Column(String(100), nullable=True)
    license_number = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class AuditLogORM(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    routing_key = Column(String(255), nullable=False)
    payload = Column(Text, nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
