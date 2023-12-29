from abc import ABC, abstractmethod


class UserBusinessEntityRedisRepositoryABC(ABC):
    @abstractmethod
    async def initialize_user_business_entity_removal(self, key_id: str, user_business_entity_id: str) -> bool:
        ...
    
    @abstractmethod
    async def retrieve_user_business_entity_removal(self, key_id: str) -> bytes:
        ...

    @abstractmethod
    async def delete_user_business_entity_removal(self, key_id: str) -> bool:
        ...
