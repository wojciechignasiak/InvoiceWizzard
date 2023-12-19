from app.kafka.events.user_events_abc import UserEventsABC
from app.kafka.events.user_business_entity_events_abc import UserBusinessEntityEventsABC


class EventsRegistry:
    __slots__= (
        'user_events',
        'user_business_entity_events'
        )

    def __init__(self,
                user_events: UserEventsABC,
                user_business_entity_events: UserBusinessEntityEventsABC) -> None:
        
        self.user_events = user_events
        self.user_business_entity_events = user_business_entity_events
        

    async def return_user_events(self, kafka_producer) -> UserEventsABC:
        return self.user_events(kafka_producer)
    
    async def return_user_business_events(self, kafka_producer) -> UserBusinessEntityEventsABC:
        return self.user_business_entity_events(kafka_producer)
