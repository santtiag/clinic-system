from datetime import datetime
from enum import Enum
from uuid import UUID

class Specialty(str, Enum):
    CARDIOLOGY = "Cardiología"
    DERMATOLOGY = "Dermatología"
    GENERAL = "Medicina General"
    PEDIATRICS = "Pediatría"

class AppointmentStatus(str, Enum):
    SCHEDULED = "programada"
    CONFIRMED = "confirmada"
    IN_ATTENTION = "en_atencion"
    COMPLETED = "completada"
    CANCELLED = "cancelada"
    CANCELLATION_REQUESTED = "cancelacion_solicitada"

class Doctor:
    def __init__(self, doctor_id: UUID, user_id: UUID, full_name: str, specialty: Specialty):
        self.doctor_id = doctor_id
        self.user_id = user_id
        self.full_name = full_name
        self.specialty = specialty

class AvailabilitySlot:
    def __init__(self, slot_id: UUID, doctor_id: UUID, start_time: datetime, end_time: datetime, is_available: bool = True):
        self.slot_id = slot_id
        self.doctor_id = doctor_id
        self.start_time = start_time
        self.end_time = end_time
        self.is_available = is_available

class Appointment:
    def __init__(self, appointment_id: UUID, patient_id: UUID, doctor_id: UUID,
                 slot_id: UUID, status: AppointmentStatus, reason: str, created_at: datetime):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.slot_id = slot_id
        self.status = status
        self.reason = reason
        self.created_at = created_at
