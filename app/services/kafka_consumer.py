import asyncio
import logging
import os

import orjson
from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s",
    handlers=[logging.StreamHandler()],
)

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "task_events")


async def run():
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        value_deserializer=lambda x: orjson.loads(x),
    )
    await consumer.start()
    try:
        logger.info(f"Consumer started. Listening on topic '{TOPIC}'...")
        async for msg in consumer:
            value = msg.value

            logger.debug(
                "Received message: topic=%s, partition=%d, offset=%d, "
                "key=%s, timestamp_ms=%d",
                msg.topic,
                msg.partition,
                msg.offset,
                msg.key,
                msg.timestamp,
            )
            logger.info(f"Event data: {value}")

    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped.")


if __name__ == "__main__":
    asyncio.run(run())
