from abc import ABC, abstractmethod


class ExternalBusinessEntityEventsABC(ABC):

    @abstractmethod
    async def remove_external_business_entity(self, id: str, email_address: str, external_business_entity_name: str):
        ...
        
    @abstractmethod
    async def external_business_entity_removed(self, email_address: str, external_business_entity_name: str):
        ...