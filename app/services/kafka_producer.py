import orjson
from aiokafka import AIOKafkaProducer

from app.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC


class KafkaProducerService:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self._producer: AIOKafkaProducer | None = None

    async def start(self):
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: orjson.dumps(v),
            )
            await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()

    async def send(self, value: dict, key: str | None = None):
        if not self._producer:
            raise RuntimeError("Kafka producer is not started")
        await self._producer.send_and_wait(
            topic=self.topic, key=(key.encode() if key else None), value=value
        )


producer = KafkaProducerService(KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC)
