import json
import os
import asyncio
from aio_pika import connect_robust, ExchangeType, Message

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://clinico:clinico_secret@rabbitmq:5672/")


async def _publish(routing_key: str, payload: dict):
    try:
        connection = await connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                "clinico.events", ExchangeType.TOPIC, durable=True
            )
            await exchange.publish(
                Message(body=json.dumps(payload, default=str).encode()),
                routing_key=routing_key,
            )
    except Exception as exc:
        print(f"Event publish error ({routing_key}): {exc}")


def publish_event(routing_key: str, payload: dict):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_publish(routing_key, payload))
        else:
            loop.run_until_complete(_publish(routing_key, payload))
    except RuntimeError:
        asyncio.run(_publish(routing_key, payload))
