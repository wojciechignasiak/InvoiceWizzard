from abc import ABC, abstractmethod
from app.schema.schema import ExternalBusinessEntity
from app.models.external_business_entity_model import (
    CreateExternalBusinessEntityModel
)

class ExternalBusinessEntityPostgresRepositoryABC(ABC):
    
    @abstractmethod
    async def create_external_business_entity(self, user_id: str, new_external_business_entity: CreateExternalBusinessEntityModel) -> ExternalBusinessEntity:
        pass