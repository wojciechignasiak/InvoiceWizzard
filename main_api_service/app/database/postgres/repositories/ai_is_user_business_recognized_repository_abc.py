from abc import ABC, abstractmethod
from app.models.ai_is_user_business_entity_recognized_model import CreateAIIsUserBusinessEntityRecognizedModel, UpdateAIIsUserBusinessEntityRecognizedModel
from app.schema.schema import AIIsUserBusinessEntityRecognized

class AIIsUserBusinessRecognizedPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_is_user_business_recognized(self, 
                                                user_id: str, 
                                                extracted_invoice_id: str, 
                                                is_user_business_recognized: CreateAIIsUserBusinessEntityRecognizedModel) -> AIIsUserBusinessEntityRecognized:
        ...

    @abstractmethod
    async def get_is_user_business_recognized(self, 
                                            extracted_invoice_id: str, 
                                            user_id: str) -> AIIsUserBusinessEntityRecognized:
        ...

    @abstractmethod
    async def update_is_user_business_recognized(self,
                                                user_id: str, 
                                                update_is_user_business_recognized: UpdateAIIsUserBusinessEntityRecognizedModel) -> None:
        ...

    @abstractmethod
    async def delete_is_user_business_recognized(self, 
                                                extracted_invoice_id: str, 
                                                user_id: str) -> bool:
        ...