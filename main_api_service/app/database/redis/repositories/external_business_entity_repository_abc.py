from abc import ABC, abstractmethod


class ExternalBusinessEntityRedisRepositoryABC(ABC):
    @abstractmethod
    async def initialize_external_business_entity_removal(self, key_id: str, user_business_entity_id: str) -> bool:
        ...
    
    @abstractmethod
    async def retrieve_external_business_entity_removal(self, key_id: str) -> bytes:
        ...

    @abstractmethod
    async def delete_external_business_entity_removal(self, key_id: str) -> bool:
        ...
