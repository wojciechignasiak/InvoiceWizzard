from abc import ABC, abstractmethod
from app.models.ai_extracted_user_business_entity_model import CreateAIExtractedUserBusinessModel, UpdateAIExtractedUserBusinessModel
from app.schema.schema import AIExtractedExternalBusinessEntity

class AIExtractedUserBusinessEntityPostgresRepositoryABC(ABC):

    @abstractmethod
    async def create_extracted_user_external_business_entity(self, 
                                                    user_id: str, 
                                                    extracted_invoice_id: str, 
                                                    ai_extracted_user_business_entity: CreateAIExtractedUserBusinessModel) -> AIExtractedExternalBusinessEntity:
        ...

    @abstractmethod
    async def get_extracted_user_external_business_entity(self, 
                                                        extracted_invoice_id: str, 
                                                        user_id: str) -> AIExtractedExternalBusinessEntity:
        ...

    @abstractmethod
    async def update_extracted_user_external_business_entity(self, 
                                                            update_extracted_user_external_business_entity: UpdateAIExtractedUserBusinessModel, 
                                                            user_id: str) -> None:
        ...

    @abstractmethod
    async def delete_extracted_user_external_business_entity(self, 
                                                            extracted_invoice_id: str, 
                                                            user_id: str) -> bool:
        ...