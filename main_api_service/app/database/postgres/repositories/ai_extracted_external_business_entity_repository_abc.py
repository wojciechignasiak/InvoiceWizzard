from abc import ABC, abstractmethod
from app.models.ai_extracted_external_business_entity_model import CreateAIExtractedExternalBusinessModel, UpdateAIExtractedExternalBusinessModel
from app.schema.schema import AIExtractedExternalBusinessEntity

class AIExtractedExternalBusinessEntityPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_extracted_external_business_entity(self, 
                                                        user_id: str, 
                                                        extracted_invoice_id: str, 
                                                        ai_extracted_external_business_entity_data: CreateAIExtractedExternalBusinessModel) -> AIExtractedExternalBusinessEntity:
        ...

    @abstractmethod
    async def get_extracted_external_business_entity(self, 
                                                    extracted_invoice_id: str, 
                                                    user_id: str) -> AIExtractedExternalBusinessEntity:
        ...

    @abstractmethod
    async def update_extracted_external_business_entity(self,
                                                        user_id: str, 
                                                        update_ai_extracted_external_business_entity: UpdateAIExtractedExternalBusinessModel) -> None:
        ...

    @abstractmethod
    async def delete_extracted_external_business_entity(self, 
                                                        extracted_invoice_id: str, 
                                                        user_id: str) -> bool:
        ...