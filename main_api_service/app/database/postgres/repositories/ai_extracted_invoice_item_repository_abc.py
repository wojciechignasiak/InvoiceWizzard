from abc import ABC, abstractmethod
from app.models.ai_extracted_invoice_item_model import CreateAIExtractedInvoiceItemModel, UpdateAIExtractedInvoiceItemModel
from app.schema.schema import AIExtractedInvoiceItem
from typing import List

class AIExtractedInvoiceItemPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_extracted_invoice_item(self,
                                            user_id: str,
                                            extracted_invoice_id: str,
                                            ai_extracted_invoice_item: CreateAIExtractedInvoiceItemModel) -> AIExtractedInvoiceItem:
        ...

    @abstractmethod
    async def get_all_extracted_invoice_item_data_by_extracted_invoice_id(self, 
                                                                        extracted_invoice_id: str,
                                                                        user_id: str) -> List[AIExtractedInvoiceItem]:
        ...

    @abstractmethod
    async def update_extracted_invoice_item(self, user_id: str, update_ai_extracted_invoice_item: UpdateAIExtractedInvoiceItemModel) -> None:
        ...

    @abstractmethod
    async def delete_extracted_invoice_item(self, extracted_invoice_item_id: str, user_id: str) -> bool:
        ...

    @abstractmethod
    async def delete_extracted_invoice_items(self, extracted_invoice_id: str, user_id: str) -> bool:
        ...