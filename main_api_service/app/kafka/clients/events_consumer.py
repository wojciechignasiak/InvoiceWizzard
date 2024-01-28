from aiokafka import AIOKafkaConsumer
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
import json
from app.kafka.consumed_events_managers.extracted_invoice_data_event_manager import ExtractedInvoiceDataMenager
from app.aplication_startup_processes import ApplicationStartupProcesses


from app.logging import logger

class EventsConsumer:
    def __init__(self, kafka_consumer: AIOKafkaConsumer):
        self.consumer: AIOKafkaConsumer = kafka_consumer

    async def run_consumer(self):
        application_startup_processes: ApplicationStartupProcesses = ApplicationStartupProcesses()
        repositories_registry: RepositoriesRegistryABC = await application_startup_processes.repositories_registry()
        extracted_invoice_data_manager: ExtractedInvoiceDataMenager = ExtractedInvoiceDataMenager(
            repositories_registry=repositories_registry,
            postgres_url=application_startup_processes.postgres_url
        )
        try:
            await self.consumer.start()
            
            async for message in self.consumer:
                try:
                    match message.topic:
                        case KafkaTopicsEnum.extracted_invoice_data.value:
                            invoice_data: str = message.value.decode("utf-8")
                            invoice_data: dict = json.loads(invoice_data)
                            await extracted_invoice_data_manager.create_invoice_data(invoice_data)
                            
                except Exception as inner_error:
                    logger.error(f"KafkaConsumer.run_consumer() inner error while processing Kafka message: {inner_error}")
        except Exception as outer_error:
            logger.error(f"KafkaConsumer.run_consumer() Error: {outer_error}")