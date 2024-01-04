from abc import ABC, abstractmethod
from app.models.ai_extracted_external_business_entity_model import CreateAIExtractedExternalBusinessModel, UpdateAIExtractedExternalBusinessModel
from app.schema.schema import AIIsExternalBusinessEntityRecognised

class AIIsExternalBusinessEntityRecognisedPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_is_external_business_entity_recognised(self, 
                                                            user_id: str, 
                                                            extracted_invoice_id: str, 
                                                            ai_extracted_external_business_entity_data: CreateAIExtractedExternalBusinessModel) -> AIIsExternalBusinessEntityRecognised:
        ...

    @abstractmethod
    async def get_is_external_business_entity_recognised(self, 
                                                        extracted_invoice_id: str, 
                                                        user_id: str) -> AIIsExternalBusinessEntityRecognised:
        ...

    @abstractmethod
    async def update_is_external_business_entity_recognised(self, 
                                                            user_id: str,
                                                            update_is_external_business_entity_recognised: UpdateAIExtractedExternalBusinessModel) -> None:
        ...

    @abstractmethod
    async def delete_is_external_business_entity_recognised(self, 
                                                            extracted_invoice_id: str, 
                                                            user_id: str) -> bool:
        ...