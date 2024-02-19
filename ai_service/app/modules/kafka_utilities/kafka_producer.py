from aiokafka import AIOKafkaProducer
from modules.logging.logging import logger
from asyncio import AbstractEventLoop
from modules.kafka_utilities.kafka_producer_abc import KafkaProducerABC
import json
import os

class KafkaProducer(KafkaProducerABC):
    def __init__(self, loop: AbstractEventLoop):
        self.host = os.getenv("KAFKA_HOST")
        self.port = os.getenv("KAFKA_PORT")
        self.producer = AIOKafkaProducer(loop=loop, bootstrap_servers=f'{self.host}:{self.port}')

    async def start_kafka_producer(self) -> None:
        try:
            await self.producer.start()
        except Exception as e:
            logger.error(f"KafkaProducer.start_kafka_producer() Error: {e}")

    async def stop_kafka_producer(self) -> None:
        try:
            await self.producer.stop()
        except Exception as e:
            logger.error(f"KafkaProducer.stop_kafka_producer() Error: {e}")

    async def extracted_invoice_data(self, extracted_data):
        try:
            await self.producer.send("extracted_invoice_data", json.dumps(extracted_data).encode('utf-8'))
        except Exception as e:
            logger.error(f"KafkaProducer.extracted_invoice_data() Error: {e}")

    async def exception_occured(self, message):
        try:
            await self.producer.send("unable_to_extract_invoice_data", json.dumps(message).encode('utf-8'))
        except Exception as e:
            logger.error(f"KafkaProducer.is_scanned() Error: {e}")