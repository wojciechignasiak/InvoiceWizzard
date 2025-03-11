#internal modules
from app.kafka.events.kafka_producer_base import KafkaProducerBase
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.custom_exceptions.custom_exceptions import EventError

#3rd party modules
from fastapi import status

#1st party modules
from typing import Protocol
import json

class IExternalBusinessEntityEvents(Protocol):

    async def remove_external_business_entity(self, id: str, email_address: str, external_business_entity_name: str) -> None:
        ...

    async def external_business_entity_removed(self, email_address: str, external_business_entity_name: str) -> None:
        ...


async def new_external_business_entity_events() -> IExternalBusinessEntityEvents:
    try:
        return ExternalBusinessEntityEvents()
    except Exception as e:
        raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while creating ExternalBusinessEntityEvents class instance",
                class_and_method="UserEvents.new_external_business_entity_events()",
                argument=None,
                child_error=e,
            )

class ExternalBusinessEntityEvents(KafkaProducerBase):

    async def remove_external_business_entity(self, id: str, email_address: str, external_business_entity_name: str) -> None:
        try:
            message = {
                "id": id, 
                "email": email_address,
                "external_business_entity_name": external_business_entity_name
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_external_business_entity.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Unexpected error occurred while creating remove external business entity event",
                    class_and_method="UserEvents.remove_external_business_entity()",
                    argument=None,
                    child_error=e,
                )
        
    async def external_business_entity_removed(self, email_address: str, external_business_entity_name: str) -> None:
        try:
            message = { 
                "email": email_address,
                "external_business_entity_name": external_business_entity_name
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_external_business_entity.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Unexpected error occurred while creating external business entity removed event",
                    class_and_method="UserEvents.external_business_entity_removed()",
                    argument=None,
                    child_error=e,
                )