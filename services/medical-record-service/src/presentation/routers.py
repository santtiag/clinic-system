from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database import SessionLocal
from src.presentation.schemas import EvolutionCreate, EvolutionResponse, MedicalRecordResponse
from src.application.services import MedicalRecordService
from src.presentation.dependencies import get_current_user

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/records/{patient_id}/evolutions", status_code=status.HTTP_201_CREATED, response_model=EvolutionResponse)
async def add_evolution(
    patient_id: UUID,
    payload: EvolutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") not in ("doctor", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only medical staff can add evolution notes")
    service = MedicalRecordService(db)
    note = await service.add_evolution(
        patient_id=patient_id,
        doctor_id=UUID(current_user["user_id"]),
        observations=payload.observations,
    )
    return EvolutionResponse(
        id=note.id,
        record_id=note.record_id,
        doctor_id=note.doctor_id,
        observations=note.observations,
        created_at=note.created_at,
    )

@router.get("/records/{patient_id}", response_model=MedicalRecordResponse)
async def get_history(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    if user_role == "patient" and str(patient_id) != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot access another patient's records")
    service = MedicalRecordService(db)
    data = await service.get_patient_history(patient_id)
    return MedicalRecordResponse(
        record_id=data["record_id"],
        patient_id=data["patient_id"],
        evolutions=[
            EvolutionResponse(
                id=e.id,
                record_id=e.record_id,
                doctor_id=e.doctor_id,
                observations=e.observations,
                created_at=e.created_at,
            ) for e in data["evolutions"]
        ],
    )
