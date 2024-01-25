from aiokafka import AIOKafkaConsumer
from modules.extract_data import ExtractData
from modules.logging.logging import logger
import asyncio
import json
import os

class KafkaSubscriber:
    def __init__(self, topic):
        self.host = os.getenv("KAFKA_HOST")
        self.port = os.getenv("KAFKA_PORT")
        self.consumer = AIOKafkaConsumer(topic, loop=asyncio.get_event_loop(), bootstrap_servers=f'{self.host}:{self.port}')

    async def run_consumer(self):
        try:
            print("Awaiting for events...")
            await self.consumer.start()
            extract_data = ExtractData()
            async for message in self.consumer:
                message = message.value.decode("utf-8")
                message = json.loads(message)
                print("Message recived!")
                
                await extract_data.is_scan_or_text(message)
        except Exception as e:
            logger.error(f"KafkaSubscriber.run_consumer() Error: {e}")
        finally:
            await self.consumer.stop()
            
