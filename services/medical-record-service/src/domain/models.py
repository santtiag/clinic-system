from datetime import datetime
from uuid import UUID

class EvolutionNote:
    def __init__(self, note_id: UUID, record_id: UUID, doctor_id: UUID,
                 observations: str, created_at: datetime):
        self.note_id = note_id
        self.record_id = record_id
        self.doctor_id = doctor_id
        self.observations = observations
        self.created_at = created_at

class MedicalRecord:
    def __init__(self, record_id: UUID, patient_id: UUID, created_at: datetime):
        self.record_id = record_id
        self.patient_id = patient_id
        self.created_at = created_at
        self.evolutions: list = []
