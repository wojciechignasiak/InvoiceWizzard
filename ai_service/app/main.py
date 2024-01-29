from modules.kafka_utilities.kafka_consumer import KafkaConsumer
from asyncio import AbstractEventLoop
import asyncio

async def main():
    try:
        print("AI Service started!")
        loop: AbstractEventLoop = asyncio.get_event_loop()
        kafka_consumer: KafkaConsumer = KafkaConsumer(
            topic="extract_invoice_data",
            loop=loop,
        )
        await kafka_consumer.run_consumer()
    finally:
        loop.stop()
        