from abc import ABC, abstractmethod
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