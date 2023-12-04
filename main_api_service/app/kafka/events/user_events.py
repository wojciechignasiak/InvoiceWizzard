from aiokafka.errors import KafkaError
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.models.kafka_topics_enum import KafkaTopicsEnum
import json
from app.logging import logger
from app.kafka.events.kafka_producer_base import KafkaProducerBase

class UserEvents(KafkaProducerBase):

    async def account_registered_event(self, id: str, email_address: str):
        try:
            message = {
                "id": id, 
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.account_registered.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"KafkaProducer.account_registered_event() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")

    async def account_confirmed_event(self, email_address: str):
        try:
            message = {
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.account_confirmed.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"KafkaProducer.account_confirmed_event() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")

    async def change_email_event(self, id: str, email_address: str):
        try:
            message = {
                "id": id,
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.change_email.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"KafkaProducer.change_email_event() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")

    async def email_changed_event(self, email_address: str):
        try:
            message = {
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.email_changed.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"KafkaProducer.email_changed_event() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")

    async def change_password_event(self, id: str, email_address: str):
        try:
            message = {
                "id": id,
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.change_password.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"KafkaProducer.change_password_event() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")

    async def reset_password_event(self, id: str, email_address: str):
        try:
            message = {
                "id": id,
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.reset_password.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"KafkaProducer.reset_password_event() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")

    async def password_changed_event(self, email_address: str):
        try:
            message = {
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.password_changed.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"KafkaProducer.password_changed_event() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")