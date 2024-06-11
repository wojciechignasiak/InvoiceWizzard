from app.kafka.events.user_events_abc import UserEventsABC
from app.kafka.events.user_business_entity_events_abc import UserBusinessEntityEventsABC
from app.kafka.events.external_business_entity_events_abc import ExternalBusinessEntityEventsABC
from app.kafka.events.invoice_events_abc import InvoiceEventsABC
from app.kafka.events.ai_invoice_events_abc import AIInvoiceEventsABC
from aiokafka import AIOKafkaProducer
from abc import ABC, abstractmethod


class EventsFactoryABC(ABC):

    @abstractmethod
    async def return_user_events(self, kafka_producer: AIOKafkaProducer) -> UserEventsABC:
        ...
    
    @abstractmethod
    async def return_user_business_events(self, kafka_producer: AIOKafkaProducer) -> UserBusinessEntityEventsABC:
        ...
    
    @abstractmethod
    async def return_external_business_events(self, kafka_producer: AIOKafkaProducer) -> ExternalBusinessEntityEventsABC:
        ...
    
    @abstractmethod
    async def return_invoice_events(self, kafka_producer: AIOKafkaProducer) -> InvoiceEventsABC:
        ...

    @abstractmethod
    async def return_ai_invoice_events(self, kafka_producer: AIOKafkaProducer) -> AIInvoiceEventsABC:
        ...