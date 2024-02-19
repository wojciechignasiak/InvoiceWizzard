from abc import ABC, abstractmethod
from app.models.ai_extraction_failure_model import CreateAIExtractionFailureModel
from app.schema.schema import AIExtractionFailure

class AIExtractionFailurePostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_ai_extraction_failure(self, 
                                            ai_extraction_failure_model: CreateAIExtractionFailureModel) -> AIExtractionFailure:
        ...

    @abstractmethod
    async def get_ai_extraction_failure(self, 
                                        ai_extraction_failure_id: str, 
                                        user_id: str) -> AIExtractionFailure:
        ...

    @abstractmethod
    async def get_all_ai_extraction_failure(self,
                                            user_id: str,
                                            page: int = 1, 
                                            items_per_page: int = 10) -> list[AIExtractionFailure]:
        ...

    @abstractmethod
    async def delete_ai_extraction_failure(self, 
                                            extracted_invoice_id: str, 
                                            user_id: str) -> bool:
        ...