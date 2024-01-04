from abc import ABC, abstractmethod
from app.models.ai_extracted_invoice_model import CreateAIExtractedInvoiceModel, UpdateAIExtractedInvoiceModel
from app.schema.schema import AIExtractedInvoice
from typing import List

class AIExtractedInvoicePostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_extracted_invoice_data(self, user_id: str, 
                                            ai_extracted_invoice: CreateAIExtractedInvoiceModel) -> AIExtractedInvoice:
        ...
    
    @abstractmethod
    async def get_extracted_invoice_data(self,
                                        extracted_invoice_id: str, 
                                        user_id: str) -> AIExtractedInvoice:
        ...

    @abstractmethod
    async def get_all_extracted_invoice_data(self, 
                                            extracted_invoice_id: str,
                                            user_id: str,
                                            page: int = 1, 
                                            items_per_page: int = 10) -> List[AIExtractedInvoice]:
        ...

    @abstractmethod
    async def update_extracted_invoice_data(self, 
                                            user_id: str,
                                            ai_update_extracted_invoice: UpdateAIExtractedInvoiceModel) -> None:
        ...

    @abstractmethod
    async def delete_extracted_invoice_data(self, extracted_invoice_id: str, user_id: str) -> bool:
        ...