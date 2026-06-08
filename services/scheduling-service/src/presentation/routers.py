from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import SessionLocal
from src.presentation.schemas import (
    AvailabilitySlotResponse, AppointmentCreate, AppointmentResponse, RescheduleRequest, StatusUpdateRequest
)
from src.application.services import SchedulingService
from src.presentation.dependencies import get_current_user

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/availability", response_model=List[AvailabilitySlotResponse])
async def list_availability(
    specialty: Optional[str] = Query(None),
    doctor_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = SchedulingService(db)
    slots = await service.search_availability(specialty, doctor_id)
    return [
        AvailabilitySlotResponse(
            id=s.id,
            doctor_id=s.doctor_id,
            start_time=s.start_time,
            end_time=s.end_time,
        ) for s in slots
    ]

@router.post("/appointments", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
async def book_appointment(
    payload: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    appt = await service.book_appointment(
        patient_id=UUID(current_user["user_id"]),
        slot_id=payload.slot_id,
        reason=payload.reason,
    )
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        slot_id=appt.slot_id,
        status=appt.status.value,
        reason=appt.reason,
        created_at=appt.created_at,
    )

@router.get("/appointments/me", response_model=List[AppointmentResponse])
async def my_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    data = await service.list_patient_appointments(UUID(current_user["user_id"]))
    return [
        AppointmentResponse(
            id=d["appointment"].id,
            patient_id=d["appointment"].patient_id,
            doctor_id=d["appointment"].doctor_id,
            slot_id=d["appointment"].slot_id,
            status=d["appointment"].status.value,
            reason=d["appointment"].reason,
            created_at=d["appointment"].created_at,
            start_time=d["slot"].start_time if d["slot"] else None,
            end_time=d["slot"].end_time if d["slot"] else None,
        ) for d in data
    ]

@router.patch("/appointments/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    appt = await service.cancel_appointment(
        appointment_id=appointment_id,
        patient_id=UUID(current_user["user_id"]),
    )
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        slot_id=appt.slot_id,
        status=appt.status.value,
        reason=appt.reason,
        created_at=appt.created_at,
    )

@router.patch("/appointments/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    payload: RescheduleRequest,
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    appt = await service.reschedule_appointment(
        appointment_id=appointment_id,
        patient_id=UUID(current_user["user_id"]),
        new_slot_id=payload.new_slot_id,
    )
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        slot_id=appt.slot_id,
        status=appt.status.value,
        reason=appt.reason,
        created_at=appt.created_at,
    )

@router.patch("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
async def update_status(
    payload: StatusUpdateRequest,
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    appt = await service.update_appointment_status(
        appointment_id=appointment_id,
        new_status=payload.status,
        user_role=current_user.get("role", ""),
    )
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        slot_id=appt.slot_id,
        status=appt.status.value,
        reason=appt.reason,
        created_at=appt.created_at,
    )

@router.get("/appointments/all", response_model=List[AppointmentResponse])
async def list_all_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("admin", "doctor", "staff"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    service = SchedulingService(db)
    appointments = await service.list_all_appointments()
    return [
        AppointmentResponse(
            id=a.id,
            patient_id=a.patient_id,
            doctor_id=a.doctor_id,
            slot_id=a.slot_id,
            status=a.status.value,
            reason=a.reason,
            created_at=a.created_at,
        ) for a in appointments
    ]
