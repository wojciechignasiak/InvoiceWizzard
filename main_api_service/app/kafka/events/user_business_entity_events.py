# internal modules
from app.kafka.events.kafka_producer_base import KafkaProducerBase
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.custom_exceptions.custom_exceptions import EventError
#3rd part modules
from fastapi import status

#1st party modules
from typing import Protocol
import json


class IUserBusinessEntityEvents(Protocol):

    async def remove_user_business_entity(self, id: str, email_address: str, user_business_entity_name: str) -> None:
        ...

    async def user_business_entity_removed(self, email_address: str, user_business_entity_name: str) -> None:
        ...

async def new_user_business_entity_events() -> IUserBusinessEntityEvents:
    try:
        return UserBusinessEntityEvents()
    except Exception as e:
        raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while creating UserBusinessEntityEvents class instance",
                class_and_method="new_user_business_entity_events()",
                argument=None,
                child_error=e,
            )
class UserBusinessEntityEvents(KafkaProducerBase):

    async def remove_user_business_entity(self, id: str, email_address: str, user_business_entity_name: str) -> None:
        try:
            message = {
                "id": id, 
                "email": email_address,
                "user_business_entity_name": user_business_entity_name
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_user_business_entity.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserBusinessEntityEvents while creating remove business entity event",
                class_and_method="UserBusinessEntityEvents.remove_user_business_entity()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )
        
    async def user_business_entity_removed(self, email_address: str, user_business_entity_name: str) -> None:
        try:
            message = { 
                "email": email_address,
                "user_business_entity_name": user_business_entity_name
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_user_business_entity.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserBusinessEntityEvents while creating user business entity removed event",
                class_and_method="UserBusinessEntityEvents.user_business_entity_removed()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )