import asyncio
import json
import logging
import os
from uuid import UUID
from aio_pika import connect_robust, ExchangeType
from src.infrastructure.database import SessionLocal
from src.application.services import BillingService

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://clinico:clinico_secret@rabbitmq:5672/")


async def _process_message(payload: dict):
    if payload.get("new_status") != "completada":
        return

    async with SessionLocal() as session:
        service = BillingService(session)
        invoice = await service.generate_invoice(
            appointment_id=UUID(payload["appointment_id"]),
            patient_id=UUID(payload["patient_id"]),
            doctor_id=UUID(payload["doctor_id"]),
        )
        logger.info(
            "Invoice generated for completed appointment %s (invoice_id=%s)",
            payload["appointment_id"],
            invoice.id,
        )


async def consume_appointment_completed():
    while True:
        try:
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
                logger.info("Billing consumer listening on appointments.status_updated")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            try:
                                payload = json.loads(message.body)
                                await _process_message(payload)
                            except Exception:
                                logger.exception(
                                    "Billing event processing error for payload: %s",
                                    message.body.decode(errors="replace"),
                                )
        except Exception:
            logger.exception("Billing consumer connection lost, retrying in 5s")
            await asyncio.sleep(5)
