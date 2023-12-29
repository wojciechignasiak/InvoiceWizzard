from app.kafka.events.external_business_entity_events_abc import ExternalBusinessEntityEventsABC
from aiokafka.errors import KafkaError
from app.kafka.events.kafka_producer_base import KafkaProducerBase
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.models.kafka_topics_enum import KafkaTopicsEnum
import json
from app.logging import logger

class ExternalBusinessEntityEvents(KafkaProducerBase, ExternalBusinessEntityEventsABC):

    async def remove_external_business_entity(self, id: str, email_address: str, external_business_entity_name: str):
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
        except KafkaError as e:
            logger.exception(f"ExternalBusinessEntityEvents.remove_external_business_entity() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")
        
    async def external_business_entity_removed(self, email_address: str, external_business_entity_name: str):
        try:
            message = { 
                "email": email_address,
                "external_business_entity_name": external_business_entity_name
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_external_business_entity.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"ExternalBusinessEntityEvents.external_business_entity_removed() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")