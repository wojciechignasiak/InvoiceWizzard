from aiokafka import AIOKafkaConsumer
from modules.extract_data import ExtractData
from modules.logging.logging import logger
from asyncio import AbstractEventLoop
from modules.kafka_utilities.kafka_consumer_abc import KafkaConsumerABC
import asyncio
import json
import os
from modules.kafka_utilities.kafka_producer import KafkaProducer

class KafkaConsumer(KafkaConsumerABC):
    def __init__(self, topic, loop: AbstractEventLoop):
        self.host = os.getenv("KAFKA_HOST")
        self.port = os.getenv("KAFKA_PORT")
        self.consumer = AIOKafkaConsumer(topic, loop=loop, bootstrap_servers=f'{self.host}:{self.port}')

    async def run_consumer(self):
        try:
            event_loop: AbstractEventLoop = asyncio.get_event_loop()
            kafka_producer = KafkaProducer(loop=event_loop)
            await kafka_producer.start_kafka_producer()

            extract_data = ExtractData(
                kafka_producer=kafka_producer,
            )
            print("Awaiting for events...")
            await self.consumer.start()
            async for message in self.consumer:
                message = message.value.decode("utf-8")
                message = json.loads(message)
                print("Message recived!")
                
                await extract_data.is_scan_or_text(message)
        except Exception as e:
            logger.error(f"KafkaConsumer.run_consumer() Error: {e}")
        finally:
            await kafka_producer.stop_kafka_producer()
            await self.consumer.stop()
            event_loop.close()
            
