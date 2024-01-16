from app.kafka.events.ai_invoice_events_abc import AIInvoiceEventsABC
from aiokafka.errors import KafkaError
from app.kafka.events.kafka_producer_base import KafkaProducerBase
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.models.kafka_topics_enum import KafkaTopicsEnum
import json
from app.logging import logger

class AIInvoiceEvents(KafkaProducerBase, AIInvoiceEventsABC):

    async def extract_invoice_data(self, file_location: str):
        try:
            message = {
                "file_location": file_location
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.extract_invoice_data.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"AIInvoiceEvents.extract_invoice_data() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")