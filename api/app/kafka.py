import json
from aiokafka import AIOKafkaProducer
from config import settings

class Kafka:
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id=settings.app_name,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def publish_order(self, payload: dict):
        assert self.producer is not None
        await self.producer.send_and_wait("orders.new", payload)

kafka = Kafka()
        
