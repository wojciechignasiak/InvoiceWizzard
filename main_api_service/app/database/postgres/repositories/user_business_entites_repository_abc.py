from abc import ABC, abstractmethod
from app.schema.schema import UserBusinessEntity
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel,
    UpdateUserBusinessEntityModel
)

class UserBusinessEntityRepositoryABC(ABC):
    @abstractmethod
    async def create_user_business_entity(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> UserBusinessEntity:
        pass

    @abstractmethod
    async def update_user_business_entity(self, user_id: str, update_user_business_entity: UpdateUserBusinessEntityModel) -> UserBusinessEntity:
        pass

    @abstractmethod
    async def remove_user_business_entity(self, user_id: str, user_business_entity_id: str) -> bool:
        pass
