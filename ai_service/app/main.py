from modules.kafka_utilities.kafka_subscriber import KafkaSubscriber
from asyncio import AbstractEventLoop
import asyncio

async def main():
    try:
        print("AI Service started!")
        loop: AbstractEventLoop = asyncio.get_event_loop()
        kafka_subscriber: KafkaSubscriber = KafkaSubscriber(
            topic="extract_invoice_data",
            loop=loop,
        )
        await kafka_subscriber.run_consumer()
    finally:
        loop.stop()
        