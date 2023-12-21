from aiokafka.errors import KafkaError
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.models.kafka_topics_enum import KafkaTopicsEnum
import json
from app.logging import logger
from app.kafka.events.kafka_producer_base import KafkaProducerBase
from app.kafka.events.invoice_events_abc import InvoiceEventsABC


class InvoiceEvents(KafkaProducerBase, InvoiceEventsABC):

    async def remove_invoice(
            self, 
            id: str, 
            email_address: str, 
            invoice_number: str,
            user_company_name: str,
            external_company_name: str,
            is_issued: str):
        try:
            message = {
                "id": id,
                "email": email_address,
                "invoice_number": invoice_number,
                "user_company_name": user_company_name,
                "external_company_name": external_company_name,
                "is_issued": is_issued
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_invoice.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"InvoiceEvents.remove_invoice() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")
        
    async def invoice_removed(
            self, 
            id: str, 
            email_address: str, 
            invoice_number: str,
            user_company_name: str,
            external_company_name: str,
            is_issued: str):
        try:
            message = {
                "id": id,
                "email": email_address,
                "invoice_number": invoice_number,
                "user_company_name": user_company_name,
                "external_company_name": external_company_name,
                "is_issued": is_issued
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.invoice_removed.value, 
                json.dumps(message).encode('utf-8')
                )
        except KafkaError as e:
            logger.exception(f"InvoiceEvents.invoice_removed() Error: {e}")
            raise KafkaBaseError("Error related to Kafka occured.")