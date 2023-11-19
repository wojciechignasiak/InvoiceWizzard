from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from app.models.kafka_topics_enum import KafkaTopicsEnum
import json
import os
import logging

class EventProducer():

    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer: AIOKafkaProducer = kafka_producer

    async def produce_event(self, topic: str, message: dict):
        try:
            await self.kafka_producer.send(topic, json.dumps(message).encode('utf-8'))
        except KafkaError as e:
            logging.exception(f"KafkaProducer.produce_event() Error: {e}")

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
            logging.exception(f"KafkaProducer.account_registered_event() Error: {e}")

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
            logging.exception(f"KafkaProducer.account_confirmed_event() Error: {e}")

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
            logging.exception(f"KafkaProducer.change_email_event() Error: {e}")

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
            logging.exception(f"KafkaProducer.email_changed_event() Error: {e}")

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
            logging.exception(f"KafkaProducer.change_password_event() Error: {e}")

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
            logging.exception(f"KafkaProducer.reset_password_event() Error: {e}")

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
            logging.exception(f"KafkaProducer.password_changed_event() Error: {e}")