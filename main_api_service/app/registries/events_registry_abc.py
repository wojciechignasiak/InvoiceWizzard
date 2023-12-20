from app.kafka.events.user_events_abc import UserEventsABC
from app.kafka.events.user_business_entity_events_abc import UserBusinessEntityEventsABC
from aiokafka import AIOKafkaProducer
from abc import ABC, abstractmethod


class EventsRegistryABC(ABC):

    @abstractmethod
    async def return_user_events(self, kafka_producer: AIOKafkaProducer) -> UserEventsABC:
        ...
    
    @abstractmethod
    async def return_user_business_events(self, kafka_producer: AIOKafkaProducer) -> UserBusinessEntityEventsABC:
        ...