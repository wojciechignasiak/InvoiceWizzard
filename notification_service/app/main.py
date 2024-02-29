from modules.kafka_utilities.kafka_consumer import KafkaConsumer
from modules.kafka_utilities.kafka_consumer_abc import KafkaConsumerABC
from asyncio import AbstractEventLoop
import asyncio

async def main():
    try:
        loop: AbstractEventLoop = asyncio.get_event_loop()
        kafka_consumer: KafkaConsumerABC = KafkaConsumer(
            loop=loop
        )
        await kafka_consumer.run_consumer()
    except Exception as e:
        print(f"Notification Service Error: {e}")
