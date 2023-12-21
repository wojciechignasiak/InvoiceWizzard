from app.kafka.events.user_events_abc import UserEventsABC
from app.kafka.events.user_business_entity_events_abc import UserBusinessEntityEventsABC
from app.kafka.events.invoice_events_abc import InvoiceEventsABC
from app.registries.events_registry_abc import EventsRegistryABC
from aiokafka import AIOKafkaProducer

class EventsRegistry(EventsRegistryABC):
    __slots__= (
        'user_events',
        'user_business_entity_events',
        'invoice_events'
        )

    def __init__(self,
                user_events: UserEventsABC,
                user_business_entity_events: UserBusinessEntityEventsABC,
                invoice_events: InvoiceEventsABC) -> None:
        
        self.user_events = user_events
        self.user_business_entity_events = user_business_entity_events
        self.invoice_events = invoice_events
        

    async def return_user_events(self, kafka_producer: AIOKafkaProducer) -> UserEventsABC:
        return self.user_events(kafka_producer)
    
    async def return_user_business_events(self, kafka_producer: AIOKafkaProducer) -> UserBusinessEntityEventsABC:
        return self.user_business_entity_events(kafka_producer)
    
    async def return_invoice_events(self, kafka_producer: AIOKafkaProducer) -> InvoiceEventsABC:
        return self.invoice_events(kafka_producer)
