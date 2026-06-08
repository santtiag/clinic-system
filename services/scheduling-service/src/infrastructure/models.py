import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database import Base
from src.domain.models import Specialty, AppointmentStatus

class DoctorORM(Base):
    __tablename__ = "doctors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=False)
    specialty = Column(
    SAEnum(
        Specialty,
        name="specialty_enum",
        values_callable=lambda enum_class: [member.value for member in enum_class],
    ),
    nullable=False,
)

class AvailabilitySlotORM(Base):
    __tablename__ = "availability_slots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

class AppointmentORM(Base):
    __tablename__ = "appointments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("availability_slots.id"), unique=True, nullable=False)
    status = Column(
    SAEnum(
        AppointmentStatus,
        name="appointment_status_enum",
        values_callable=lambda enum_class: [member.value for member in enum_class],
    ),
    default=AppointmentStatus.SCHEDULED,
    nullable=False,
)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
