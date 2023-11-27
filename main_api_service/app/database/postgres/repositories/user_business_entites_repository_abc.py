from abc import ABC, abstractmethod
from app.schema.schema import UserBusinessEntity
from app.models.user_business_entity_model import CreateUserBusinessEntityModel

class UserBusinessEntityRepositoryABC(ABC):
    @abstractmethod
    async def create_user_business_entity(self, user_id: str, new_business: CreateUserBusinessEntityModel) -> UserBusinessEntity:
        pass