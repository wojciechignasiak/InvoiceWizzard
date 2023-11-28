from abc import ABC, abstractmethod


class UserBusinessEntitiesRedisRepositoryABC(ABC):
    @abstractmethod
    async def initialize_user_business_entity_removal(self, key_id: str, user_business_entity_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_user_business_entity_removal(self, key_id: str) -> bytes:
        pass

    @abstractmethod
    async def delete_user_business_entity_removal(self, key_id: str) -> bool:
        pass
