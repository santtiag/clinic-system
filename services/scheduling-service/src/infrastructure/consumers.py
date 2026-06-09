import asyncio
import json
import os
from uuid import UUID

from aio_pika import connect_robust, ExchangeType

from src.infrastructure.database import SessionLocal
from src.infrastructure.repositories import DoctorRepository

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://clinico:clinico_secret@rabbitmq:5672/")

# Mapeo entre la especialidad libre de identity y los valores del enum de scheduling.
SPECIALTY_ALIASES = {
    "cardiologia": "Cardiología",
    "cardiología": "Cardiología",
    "cardiology": "Cardiología",
    "dermatologia": "Dermatología",
    "dermatología": "Dermatología",
    "dermatology": "Dermatología",
    "medicina general": "Medicina General",
    "general": "Medicina General",
    "pediatria": "Pediatría",
    "pediatría": "Pediatría",
    "pediatrics": "Pediatría",
}


def _normalize_specialty(value: str | None) -> str | None:
    if not value:
        return None
    return SPECIALTY_ALIASES.get(value.strip().lower(), value)


async def _handle_doctor_registered(payload: dict) -> None:
    user_id = payload.get("user_id")
    full_name = payload.get("full_name") or payload.get("username") or "Médico"
    specialty = _normalize_specialty(payload.get("specialty"))
    if not user_id or not specialty:
        print(f"doctor.registered ignored, missing data: {payload}")
        return
    async with SessionLocal() as session:
        repo = DoctorRepository(session)
        await repo.upsert(UUID(user_id), full_name, specialty)
        print(f"Doctor synced from identity: {full_name} ({specialty})")


async def consume_doctor_events() -> None:
    while True:
        try:
            connection = await connect_robust(RABBITMQ_URL)
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                "clinico.events", ExchangeType.TOPIC, durable=True
            )
            queue = await channel.declare_queue(
                "scheduling.doctor.registered", durable=True
            )
            await queue.bind(exchange, routing_key="doctor.registered")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            payload = json.loads(message.body.decode())
                            await _handle_doctor_registered(payload)
                        except Exception as exc:  # noqa: BLE001
                            print(f"Failed to process doctor.registered: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"Consumer connection failed, retrying in 5s: {exc}")
            await asyncio.sleep(5)
