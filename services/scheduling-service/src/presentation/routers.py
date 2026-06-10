from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import SessionLocal
from src.presentation.schemas import (
    AvailabilitySlotResponse, AppointmentCreate, AppointmentResponse,
    RescheduleRequest, StatusUpdateRequest, StatusHistoryResponse,
    AssignDoctorRequest, DoctorResponse,
)
from src.application.services import SchedulingService
from src.presentation.dependencies import (
    get_current_user, require_medical_staff, require_staff,
)

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session


def _appt_response(item: dict) -> AppointmentResponse:
    appt = item["appointment"]
    slot = item.get("slot")
    doctor = item.get("doctor")
    return AppointmentResponse(
        id=appt.id,
        patient_id=appt.patient_id,
        doctor_id=appt.doctor_id,
        slot_id=appt.slot_id,
        status=appt.status.value,
        reason=appt.reason,
        created_at=appt.created_at,
        start_time=slot.start_time if slot else None,
        end_time=slot.end_time if slot else None,
        doctor_name=doctor.full_name if doctor else None,
        specialty=(
            doctor.specialty.value if doctor and hasattr(doctor.specialty, "value")
            else (doctor.specialty if doctor else None)
        ),
    )


@router.get("/availability", response_model=List[AvailabilitySlotResponse])
async def list_availability(
    specialty: Optional[str] = Query(None),
    doctor_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = SchedulingService(db)
    slots = await service.search_availability(specialty, doctor_id)
    doctors = await service._doctor_map()
    result = []
    for s in slots:
        doctor = doctors.get(s.doctor_id)
        result.append(AvailabilitySlotResponse(
            id=s.id,
            doctor_id=s.doctor_id,
            start_time=s.start_time,
            end_time=s.end_time,
            doctor_name=doctor.full_name if doctor else None,
            specialty=(
                doctor.specialty.value if doctor and hasattr(doctor.specialty, "value")
                else (doctor.specialty if doctor else None)
            ),
        ))
    return result


@router.get("/doctors", response_model=List[DoctorResponse])
async def list_doctors(
    specialty: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    doctors = await service.list_doctors(specialty)
    return [
        DoctorResponse(
            id=d.id,
            user_id=d.user_id,
            full_name=d.full_name,
            specialty=d.specialty.value if hasattr(d.specialty, "value") else d.specialty,
        ) for d in doctors
    ]

@router.post("/appointments", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
async def book_appointment(
    payload: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    role = current_user.get("role")
    if role in ("staff", "admin"):
        if not payload.patient_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "patient_id required for staff booking")
        patient_id = payload.patient_id
    else:
        patient_id = UUID(current_user["user_id"])
    service = SchedulingService(db)
    appt = await service.book_appointment(
        patient_id=patient_id,
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
    role = current_user.get("role")
    user_id = UUID(current_user["user_id"])
    if role == "doctor":
        data = await service.list_doctor_appointments(user_id)
    else:
        data = await service.list_patient_appointments(user_id)
    return [_appt_response(d) for d in data]

@router.post("/appointments/{appointment_id}/cancellation-request", response_model=AppointmentResponse)
async def request_cancellation(
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "patient":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only patients can request cancellation")
    service = SchedulingService(db)
    appt = await service.request_cancellation(
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


@router.post("/appointments/{appointment_id}/cancellation-request/confirm", response_model=AppointmentResponse)
async def confirm_cancellation(
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_staff),
):
    service = SchedulingService(db)
    appt = await service.confirm_cancellation(
        appointment_id=appointment_id,
        user_id=UUID(current_user["user_id"]) if current_user.get("user_id") else None,
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


@router.post("/appointments/{appointment_id}/cancellation-request/reject", response_model=AppointmentResponse)
async def reject_cancellation(
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_staff),
):
    service = SchedulingService(db)
    appt = await service.reject_cancellation(
        appointment_id=appointment_id,
        user_id=UUID(current_user["user_id"]) if current_user.get("user_id") else None,
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


@router.patch("/appointments/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    role = current_user.get("role", "")
    if role == "patient":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Patients must use the cancellation request endpoint",
        )
    appt = await service.cancel_appointment(
        appointment_id=appointment_id,
        patient_id=None,
        user_role=role,
        enforce_window=False,
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
    current_user: dict = Depends(require_staff),
):
    service = SchedulingService(db)
    appt = await service.reschedule_appointment(
        appointment_id=appointment_id,
        new_slot_id=payload.new_slot_id,
        user_id=UUID(current_user["user_id"]) if current_user.get("user_id") else None,
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


@router.patch("/appointments/{appointment_id}/assign", response_model=AppointmentResponse)
async def assign_doctor(
    payload: AssignDoctorRequest,
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_staff),
):
    service = SchedulingService(db)
    appt = await service.assign_doctor(
        appointment_id=appointment_id,
        doctor_id=payload.doctor_id,
        user_id=UUID(current_user["user_id"]) if current_user.get("user_id") else None,
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

@router.patch("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
async def update_status(
    payload: StatusUpdateRequest,
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_medical_staff),
):
    service = SchedulingService(db)
    user_id = UUID(current_user["user_id"]) if current_user.get("user_id") else None
    appt = await service.update_appointment_status(
        appointment_id=appointment_id,
        new_status=payload.status,
        user_role=current_user.get("role", ""),
        user_id=user_id,
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

@router.get("/appointments/{appointment_id}/history", response_model=List[StatusHistoryResponse])
async def appointment_history(
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_medical_staff),
):
    service = SchedulingService(db)
    history = await service.get_status_history(appointment_id)
    return [
        StatusHistoryResponse(
            id=h.id,
            appointment_id=h.appointment_id,
            old_status=h.old_status,
            new_status=h.new_status,
            changed_by=h.changed_by,
            changed_by_role=h.changed_by_role,
            changed_at=h.changed_at,
        ) for h in history
    ]

@router.get("/appointments/all", response_model=List[AppointmentResponse])
async def list_all_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_medical_staff),
):
    service = SchedulingService(db)
    role = current_user.get("role")
    if role == "doctor":
        data = await service.list_doctor_appointments(UUID(current_user["user_id"]))
    else:
        data = await service.list_all_appointments_enriched()
    return [_appt_response(d) for d in data]


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SchedulingService(db)
    appt = await service._appointments.get_by_id(appointment_id)
    if not appt:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
    role = current_user.get("role")
    if role == "patient" and str(appt.patient_id) != current_user.get("user_id"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Appointment not found")
    slot = await service._slots.get_by_id(appt.slot_id)
    doctor = await service._doctors.get_by_id(appt.doctor_id)
    return _appt_response({"appointment": appt, "slot": slot, "doctor": doctor})
