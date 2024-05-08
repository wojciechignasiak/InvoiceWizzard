from abc import ABC, abstractmethod
from typing import Optional
from app.schema.schema import UserBusinessEntity
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel,
    UpdateUserBusinessEntityModel
)

class UserBusinessEntityPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_user_business_entity(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> UserBusinessEntity:
        ...

    @abstractmethod
    async def is_user_business_entity_unique(self, user_id: str, new_user_business_entity: CreateUserBusinessEntityModel) -> bool:
        ...

    @abstractmethod
    async def update_user_business_entity(self, user_id: str, update_user_business_entity: UpdateUserBusinessEntityModel) -> UserBusinessEntity:
        ...
    
    @abstractmethod
    async def is_user_business_entity_unique_beside_one_to_update(self, user_id: str, update_user_business_entity: UpdateUserBusinessEntityModel) -> bool:
        ...

    @abstractmethod
    async def remove_user_business_entity(self, user_id: str, user_business_entity_id: str) -> bool:
        ...

    @abstractmethod
    async def get_user_business_entity(self, user_id: str, user_business_entity_id: str) -> UserBusinessEntity:
        ...

    @abstractmethod
    async def get_all_user_business_entities(self, user_id: str,
                                            page: int = 1, 
                                            items_per_page: int = 10,
                                            company_name: Optional[str] = None,
                                            city: Optional[str] = None,
                                            postal_code: Optional[str] = None,
                                            street: Optional[str] = None,
                                            nip: Optional[str] = None,
                                            krs: Optional[str] = None) -> list:
        ...