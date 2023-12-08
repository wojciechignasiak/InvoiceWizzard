from abc import ABC, abstractmethod
from typing import Optional
from app.schema.schema import ExternalBusinessEntity
from app.models.external_business_entity_model import (
    CreateExternalBusinessEntityModel,
    UpdateExternalBusinessEntityModel
)

class ExternalBusinessEntityPostgresRepositoryABC(ABC):
    
    @abstractmethod
    async def create_external_business_entity(self, user_id: str, new_external_business_entity: CreateExternalBusinessEntityModel) -> ExternalBusinessEntity:
        pass

    @abstractmethod
    async def is_external_business_entity_unique(self, user_id: str, new_external_business_entity: CreateExternalBusinessEntityModel) -> bool:
        pass

    @abstractmethod
    async def update_external_business_entity(self, user_id: str, update_external_business_entity: UpdateExternalBusinessEntityModel) -> ExternalBusinessEntity:
        pass

    @abstractmethod
    async def is_external_business_entity_unique_beside_one_to_update(self, user_id: str, update_external_business_entity: UpdateExternalBusinessEntityModel) -> bool:
        pass

    @abstractmethod
    async def get_external_business_entity(self, user_id: str, external_business_entity_id: str) -> ExternalBusinessEntity:
        pass

    @abstractmethod
    async def get_all_external_business_entities(self, user_id: str, 
                                                page: int = 1, 
                                                items_per_page: int = 10,
                                                company_name: Optional[str] = None,
                                                city: Optional[str] = None,
                                                postal_code: Optional[str] = None,
                                                street: Optional[str] = None,
                                                nip: Optional[str] = None,
                                                krs: Optional[str] = None) -> list:
        pass

    @abstractmethod
    async def remove_external_business_entity(self, user_id: str, external_business_entity_id: str) -> bool:
        pass