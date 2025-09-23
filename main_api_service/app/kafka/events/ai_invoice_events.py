#internal modules
from app.kafka.events.kafka_producer_base import KafkaProducerBase
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.custom_exceptions.custom_exceptions import EventError

#3rd party modules
from fastapi import status

#1st party modules
from typing import Protocol
import json

class IAIInvoiceEvents(Protocol):

    async def extract_invoice_data(self, file_location: str, user_business_entities_nip: str) -> None:
        ...

def new_ai_invoice_events() -> IAIInvoiceEvents:
    try:
        return AIInvoiceEvents()
    except Exception as e:
        pass

class AIInvoiceEvents(KafkaProducerBase, IAIInvoiceEvents):

    async def extract_invoice_data(self, file_location: str, user_business_entities_nip: str) -> None:
        try:
            message = {
                "file_location": file_location,
                "user_business_entities_nip": user_business_entities_nip,
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.extract_invoice_data.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Unexpected error occurred while creating ExternalBusinessEntityEvents class instance",
                    class_and_method="UserEvents.new_external_business_entity_events()",
                    argument=None,
                    child_error=e,
                )