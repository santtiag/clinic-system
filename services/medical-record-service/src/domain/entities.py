"""
Domain entities for Medical Record Service.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum

from sqlalchemy import (
    Column, String, DateTime, Boolean, Enum as SQLEnum,
    ForeignKey, Text, Integer, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from common.database import BaseModel


class ClinicalNoteType(str, Enum):
    """Type of clinical note."""
    CONSULTATION = "consultation"
    EVOLUTION = "evolution"
    EMERGENCY = "emergency"
    PROCEDURE = "procedure"
    LAB_RESULT = "lab_result"


class MedicalRecord(BaseModel):
    """Medical record root aggregate."""
    __tablename__ = "medical_records"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(PGUUID(as_uuid=True), nullable=False, unique=True, index=True)
    record_number = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    clinical_notes = relationship("ClinicalNote", back_populates="medical_record", order_by="ClinicalNote.created_at.desc()")

    __table_args__ = (
        Index("ix_medical_records_patient", "patient_id"),
    )


class ClinicalNote(BaseModel):
    """Clinical note / consultation record."""
    __tablename__ = "clinical_notes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    medical_record_id = Column(PGUUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False, index=True)
    doctor_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    appointment_id = Column(PGUUID(as_uuid=True), nullable=True, index=True)
    note_type = Column(SQLEnum(ClinicalNoteType), nullable=False, default=ClinicalNoteType.CONSULTATION)
    chief_complaint = Column(Text, nullable=True)  # Motivo de consulta
    present_illness = Column(Text, nullable=True)  # Enfermedad actual
    physical_exam = Column(Text, nullable=True)  # Examen físico
    evolution = Column(Text, nullable=True)  # Evolución
    observations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="clinical_notes")
    diagnoses = relationship("Diagnosis", back_populates="clinical_note", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="clinical_note", cascade="all, delete-orphan")
    documents = relationship("MedicalDocument", back_populates="clinical_note", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_clinical_notes_medical_record", "medical_record_id"),
        Index("ix_clinical_notes_doctor", "doctor_id"),
    )


class Diagnosis(BaseModel):
    """Diagnosis entry with CIE-10 code."""
    __tablename__ = "diagnoses"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    clinical_note_id = Column(PGUUID(as_uuid=True), ForeignKey("clinical_notes.id"), nullable=False, index=True)
    cie10_code = Column(String(10), nullable=False, index=True)
    description = Column(Text, nullable=False)
    diagnosis_type = Column(String(20), nullable=False, default="principal")  # principal, secundario, diferencial
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    clinical_note = relationship("ClinicalNote", back_populates="diagnoses")

    __table_args__ = (
        Index("ix_diagnoses_cie10", "cie10_code"),
    )


class Prescription(BaseModel):
    """Medical prescription."""
    __tablename__ = "prescriptions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    clinical_note_id = Column(PGUUID(as_uuid=True), ForeignKey("clinical_notes.id"), nullable=False, index=True)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)  # Ej: "cada 8 horas"
    duration = Column(String(100), nullable=False)  # Ej: "7 días"
    route = Column(String(50), nullable=True)  # vía de administración
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    clinical_note = relationship("ClinicalNote", back_populates="prescriptions")


class MedicalDocument(BaseModel):
    """Attached medical document (PDF, image, DICOM)."""
    __tablename__ = "medical_documents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    clinical_note_id = Column(PGUUID(as_uuid=True), ForeignKey("clinical_notes.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, jpeg, png, dicom
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    uploaded_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    clinical_note = relationship("ClinicalNote", back_populates="documents")
