from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.models.kafka_topics_enum import KafkaTopicsEnum
import json
from app.logging import logger

class UserBusinessEntityEvents:

    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer: AIOKafkaProducer = kafka_producer

    async def remove_user_business_entity(self, id: str, email_address: str, user_business_entity_name: str):
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
        except KafkaError as e:
            logger.exception(f"UserBusinessEntityEvents.remove_user_business_entity() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")
        
    async def user_business_entity_removed(self, email_address: str, user_business_entity_name: str):
        try:
            message = { 
                "email": email_address,
                "user_business_entity_name": user_business_entity_name
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_user_business_entity.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"UserBusinessEntityEvents.user_business_entity_removed() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")