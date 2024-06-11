from app.kafka.events.user_events_abc import UserEventsABC
from app.kafka.events.user_business_entity_events_abc import UserBusinessEntityEventsABC
from app.kafka.events.external_business_entity_events_abc import ExternalBusinessEntityEventsABC
from app.kafka.events.invoice_events_abc import InvoiceEventsABC
from app.kafka.events.ai_invoice_events_abc import AIInvoiceEventsABC
from app.factories.events_factory_abc import EventsFactoryABC

class EventsFactory(EventsFactoryABC):
    __slots__= (
        '__user_events',
        '__user_business_entity_events',
        '__external_business_entity_events',
        '__invoice_events',
        '__ai_invoice_events'
        )

    def __init__(
            self,
            user_events: UserEventsABC,
            user_business_entity_events: UserBusinessEntityEventsABC,
            external_business_entity_events: ExternalBusinessEntityEventsABC,
            invoice_events: InvoiceEventsABC,
            ai_invoice_events: AIInvoiceEventsABC,
            ) -> None:
        
        self.__user_events = user_events
        self.__user_business_entity_events = user_business_entity_events
        self.__external_business_entity_events = external_business_entity_events
        self.__invoice_events = invoice_events
        self.__ai_invoice_events = ai_invoice_events
        

    async def return_user_events(self) -> UserEventsABC:
        return self.__user_events()
    
    async def return_user_business_events(self) -> UserBusinessEntityEventsABC:
        return self.__user_business_entity_events()
    
    async def return_external_business_events(self) -> ExternalBusinessEntityEventsABC:
        return self.__external_business_entity_events()
    
    async def return_invoice_events(self) -> InvoiceEventsABC:
        return self.__invoice_events()
    
    async def return_ai_invoice_events(self) -> AIInvoiceEventsABC:
        return self.__ai_invoice_events()