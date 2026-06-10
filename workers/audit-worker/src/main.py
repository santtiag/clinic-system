import asyncio
import json
import os
import logging
from aio_pika import connect_robust, ExchangeType
from src.infrastructure.database import init_db, SessionLocal
from src.infrastructure.repository import AuditRepository

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://clinico:clinico_secret@rabbitmq:5672/")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("audit-worker")


async def connect_with_retry(url: str, max_attempts: int = 30, delay: float = 2.0):
    for attempt in range(1, max_attempts + 1):
        try:
            return await connect_robust(url)
        except Exception as exc:
            if attempt == max_attempts:
                raise
            logger.warning(
                "RabbitMQ no disponible (intento %s/%s): %s. Reintentando en %ss...",
                attempt,
                max_attempts,
                exc,
                delay,
            )
            await asyncio.sleep(delay)


async def process_event(routing_key: str, payload: dict):
    event_type = routing_key.split(".")[0]
    async with SessionLocal() as session:
        repo = AuditRepository(session)
        await repo.create(
            event_type=event_type,
            routing_key=routing_key,
            payload=json.dumps(payload, default=str),
        )
    logger.info(f"📝 Audit log guardado: {routing_key}")


async def run():
    await init_db()
    connection = await connect_with_retry(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "clinico.events", ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue("audit.all_events", durable=True)
        # Escucha wildcard appointments.* e invoices.*
        await queue.bind(exchange, "appointments.*")
        await queue.bind(exchange, "invoices.*")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        payload = json.loads(message.body)
                        await process_event(message.routing_key, payload)
                    except Exception as e:
                        logger.error(f"Error en audit worker: {e}")


if __name__ == "__main__":
    asyncio.run(run())
