from aiokafka import AIOKafkaConsumer
from modules.extract_data import extract_data
import asyncio
import json
import os

class KafkaSubscriber():
    def __init__(self, topic):
        self.host = os.getenv('KAFKA_HOST')
        self.port = os.getenv('KAFKA_PORT')
        self.consumer = AIOKafkaConsumer(topic, loop=asyncio.get_event_loop(), bootstrap_servers=f'{self.host}:{self.port}')

    async def run_consumer(self):
        try:
            print("Awaiting for events...")
            await self.consumer.start()
            async for message in self.consumer:
                message = message.value.decode("utf-8")
                message = json.loads(message)
                print("Message recived!")
                loop = asyncio.get_event_loop()
                await loop.create_task(extract_data(message))
        finally:
            await self.consumer.stop()
            
