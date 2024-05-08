from abc import ABC, abstractmethod
from app.models.ai_extracted_external_business_entity_model import CreateAIExtractedExternalBusinessModel, UpdateAIExtractedExternalBusinessModel
from app.schema.schema import AIIsExternalBusinessEntityRecognized

class AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_is_external_business_entity_recognized(self, 
                                                            user_id: str, 
                                                            extracted_invoice_id: str, 
                                                            ai_extracted_external_business_entity_data: CreateAIExtractedExternalBusinessModel) -> AIIsExternalBusinessEntityRecognized:
        ...

    @abstractmethod
    async def get_is_external_business_entity_recognized(self, 
                                                        extracted_invoice_id: str, 
                                                        user_id: str) -> AIIsExternalBusinessEntityRecognized:
        ...

    @abstractmethod
    async def update_is_external_business_entity_recognized(self, 
                                                            user_id: str,
                                                            update_is_external_business_entity_recognized: UpdateAIExtractedExternalBusinessModel) -> None:
        ...

    @abstractmethod
    async def delete_is_external_business_entity_recognized(self, 
                                                            extracted_invoice_id: str, 
                                                            user_id: str) -> bool:
        ...