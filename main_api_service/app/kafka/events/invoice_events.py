#internal modules
from main_api_service.app.models.kafka_topics_enum import KafkaTopicsEnum
from main_api_service.app.kafka.events.kafka_producer_base import KafkaProducerBase
from main_api_service.app.custom_exceptions.custom_exceptions import EventError

#3rd party modules
from fastapi import status

#1st party modules
from typing import Protocol
import json
from uuid import UUID


class IInvoiceEvents(Protocol):

    async def remove_invoice(
                self, 
                key_id: UUID,
                email_address: str, 
                invoice_number: str,
                user_company_name: str,
                external_business_entity_name: str,
                is_issued: bool) -> None: 
        ...
    
    async def invoice_removed(
            self, 
            key_id: UUID,
            email_address: str, 
            invoice_number: str,
            user_company_name: str,
            external_business_entity_name: str,
            is_issued: bool) -> None:
        ...

async def new_invoice_events() -> IInvoiceEvents:
    try:
        return InvoiceEvents()
    except Exception as e:
        raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while creating InvoiceEvent class instance",
                class_and_method="new_invoice_events()",
                argument=None,
                child_error=e,
            )

class InvoiceEvents(KafkaProducerBase, IInvoiceEvents):

    async def remove_invoice(
            self, 
            key_id: UUID,
            email_address: str, 
            invoice_number: str,
            user_company_name: str,
            external_business_entity_name: str,
            is_issued: bool) -> None: 
        try:
            message = {
                "key_id": key_id,
                "email": email_address,
                "invoice_number": invoice_number,
                "user_company_name": user_company_name,
                "external_business_entity_name": external_business_entity_name,
                "is_issued": is_issued
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.remove_invoice.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceEvents while creating remove invoice event",
                class_and_method="UserEvents.remove_invoice()",
                argument={
                    "key_id": key_id,
                    'email_address': email_address, 
                    'invoice_number': invoice_number, 
                    'user_company_name': user_company_name,
                    'external_business_entity_name': external_business_entity_name,
                    'is_issued': is_issued
                    },
                child_error=e,
            )
        
    async def invoice_removed(
            self, 
            key_id: UUID,
            email_address: str, 
            invoice_number: str,
            user_company_name: str,
            external_business_entity_name: str,
            is_issued: bool) -> None:
        try:
            message = {
                "key_id": key_id,
                "email": email_address,
                "invoice_number": invoice_number,
                "user_company_name": user_company_name,
                "external_business_entity_name": external_business_entity_name,
                "is_issued": is_issued
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.invoice_removed.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceEvents while creating invoice removed event",
                class_and_method="UserEvents.invoice_removed()",
                argument={
                    "key_id": key_id,
                    'email_address': email_address, 
                    'invoice_number': invoice_number, 
                    'user_company_name': user_company_name,
                    'external_business_entity_name': external_business_entity_name,
                    'is_issued': is_issued
                    },
                child_error=e,
            )