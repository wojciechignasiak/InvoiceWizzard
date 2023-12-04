from abc import ABC, abstractmethod
from app.schema.schema import UserBusinessEntity
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel,
    UpdateUserBusinessEntityModel
)

class UserBusinessEntityPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_user_business_entity(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> UserBusinessEntity:
        pass

    @abstractmethod
    async def is_user_business_entity_unique(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> bool:
        pass

    @abstractmethod
    async def update_user_business_entity(self, user_id: str, update_user_business_entity: UpdateUserBusinessEntityModel) -> UserBusinessEntity:
        pass
    
    @abstractmethod
    async def is_user_business_entity_unique_beside_one_to_update(self, user_id: str, update_user_business_entity: UpdateUserBusinessEntityModel) -> bool:
        pass

    @abstractmethod
    async def remove_user_business_entity(self, user_id: str, user_business_entity_id: str) -> bool:
        pass

    @abstractmethod
    async def get_user_business_entity(self, user_id: str, user_business_entity_id: str) -> UserBusinessEntity:
        pass

    @abstractmethod
    async def get_all_user_business_entities(self, user_id: str) -> list:
        pass