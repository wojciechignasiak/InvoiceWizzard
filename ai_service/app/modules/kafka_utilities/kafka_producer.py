import os
from aiokafka import AIOKafkaProducer
from modules.logging.logging import logger
import asyncio
import json

class KafkaProducer:
    def __init__(self):
        self.host = os.getenv("KAFKA_HOST")
        self.port = os.getenv("KAFKA_PORT")
        self.producer = AIOKafkaProducer(loop=asyncio.get_event_loop(), bootstrap_servers=f'{self.host}:{self.port}')

    async def extracted_invoice_data(self, extracted_data):
        try:
            await self.producer.start()
            await self.producer.send("extracted_invoice_data", json.dumps(extracted_data).encode('utf-8'))
        except Exception as e:
            logger.error(f"KafkaProducer.extracted_invoice_data() Error: {e}")
        finally:
            await self.producer.stop()
            
    async def is_scanned(self, message):
        try:
            await self.producer.start()
            await self.producer.send("unable_to_extract_invoice_data", json.dumps(message).encode('utf-8'))
        except Exception as e:
            logger.error(f"KafkaProducer.is_scanned() Error: {e}")
        finally:
            await self.producer.stop()