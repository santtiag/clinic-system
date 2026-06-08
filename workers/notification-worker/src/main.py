import asyncio
import json
import os
import logging
from aio_pika import connect_robust, ExchangeType

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://clinico:clinico_secret@rabbitmq:5672/")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("notification-worker")

async def process_notification(routing_key: str, payload: dict):
    if routing_key == "appointments.cancelled":
        logger.info(
            f"📧 [EMAIL/SMS] Cita {payload['appointment_id']} cancelada. "
            f"Notificar paciente {payload.get('patient_id')} y médico."
        )
    elif routing_key == "appointments.rescheduled":
        logger.info(
            f"📧 [EMAIL/SMS] Cita {payload['appointment_id']} reprogramada. "
            f"Nuevo slot: {payload.get('new_slot_id')}"
        )
    elif routing_key == "appointments.status_updated":
        logger.info(
            f"📧 [EMAIL/SMS] Cita {payload['appointment_id']} pasó a estado '{payload['new_status']}'. "
            f"Notificar a paciente {payload.get('patient_id')}."
        )
    else:
        logger.info(f"📧 Notificación genérica: {routing_key} | {payload}")

async def run():
    connection = await connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "clinico.events", ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue("notifications.general", durable=True)
        await queue.bind(exchange, "appointments.cancelled")
        await queue.bind(exchange, "appointments.rescheduled")
        await queue.bind(exchange, "appointments.status_updated")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body)
                        await process_notification(message.routing_key, payload)
                    except Exception as e:
                        logger.error(f"Error procesando notificación: {e}")

if __name__ == "__main__":
    asyncio.run(run())
