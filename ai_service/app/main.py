from modules.kafka_utilities.kafka_consumer import KafkaConsumer
from modules.kafka_utilities.kafka_consumer_abc import KafkaConsumerABC
from modules.initialize_models_utility.initialize_models_abc import InitializeModelsABC
from modules.initialize_models_utility.initialize_models import InitializeModels
from asyncio import AbstractEventLoop
import asyncio

async def main():
    try:
        initialize_models: InitializeModelsABC = InitializeModels()
        await initialize_models.initialize_models()
        loop: AbstractEventLoop = asyncio.get_event_loop()
        kafka_consumer: KafkaConsumerABC = KafkaConsumer(
            topic="extract_invoice_data",
            loop=loop,
        )
        print("AI Service started!")
        await kafka_consumer.run_consumer()
    except Exception as e:
        print(f"AI Service Error: {e}")
