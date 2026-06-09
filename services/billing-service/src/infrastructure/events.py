import asyncio
import json
import os
from uuid import UUID
from aio_pika import connect_robust, ExchangeType
from src.infrastructure.database import SessionLocal
from src.application.services import BillingService

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://clinico:clinico_secret@rabbitmq:5672/")

async def consume_appointment_completed():
    connection = await connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "clinico.events", ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(
            "billing.appointments.completed", durable=True
        )
        await queue.bind(exchange, routing_key="appointments.status_updated")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body)
                        if payload.get("new_status") == "completada":
                            async with SessionLocal() as session:
                                service = BillingService(session)
                                await service.generate_invoice(
                                    appointment_id=UUID(payload["appointment_id"]),
                                    patient_id=UUID(payload["patient_id"]),
                                    doctor_id=UUID(payload["doctor_id"]),
                                )
                    except Exception as e:
                        print(f"Billing event processing error: {e}")
