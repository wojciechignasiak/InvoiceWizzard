from aiokafka import AIOKafkaConsumer
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.kafka.consumed_events_managers.extracted_invoice_data_event_manager_abc import ExtractedInvoiceDataMenagerABC
from app.logging import logger
from typing import Dict

import json

class EventsConsumer:
    def __init__(self, 
                kafka_consumer: AIOKafkaConsumer,
                extracted_invoice_data_event_manager: ExtractedInvoiceDataMenagerABC):
        self._consumer: AIOKafkaConsumer = kafka_consumer
        self._extracted_invoice_data_event_manager: ExtractedInvoiceDataMenagerABC = extracted_invoice_data_event_manager
        

    async def run_consumer(self):
        try:
            await self._consumer.start()
            async for message in self._consumer:
                try:
                    match message.topic:
                        case KafkaTopicsEnum.extracted_invoice_data.value:
                            invoice_data: str = message.value.decode("utf-8")
                            invoice_data: Dict = json.loads(invoice_data)
                            await self._extracted_invoice_data_event_manager.create_invoice_data(invoice_data)
                        case KafkaTopicsEnum.unable_to_extract_invoice_data.value:
                            invoice_data: str = message.value.decode("utf-8")
                            invoice_data: Dict = json.loads(invoice_data)
                            await self._extracted_invoice_data_event_manager.create_invoice_data(invoice_data)
                            
                except Exception as inner_error:
                    logger.error(f"KafkaConsumer.run_consumer() inner error while processing Kafka message: {inner_error}")
        except Exception as outer_error:
            logger.error(f"KafkaConsumer.run_consumer() Error: {outer_error}")