import json
import os
from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://clinico:clinico_secret@rabbitmq:5672/")

async def publish_event(routing_key: str, payload: dict):
    try:
        connection = await connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                "clinico.events", ExchangeType.TOPIC, durable=True
            )
            queue = await channel.declare_queue(f"events.{routing_key}", durable=True)
            await queue.bind(exchange, routing_key=routing_key)
            msg = Message(
                body=json.dumps(payload, default=str).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            await exchange.publish(msg, routing_key=routing_key)
    except Exception as e:
        # En producción: retry / dead-letter / log estructurado
        print(f"Event publish failed: {e}")
