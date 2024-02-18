from app.models.ai_extracted_invoice_model import AIExtractedInvoiceModel
from app.models.ai_extracted_invoice_model import CreateAIExtractedInvoiceModel
from app.models.ai_extracted_invoice_item_model import CreateAIExtractedInvoiceItemModel
from app.models.ai_extracted_user_business_entity_model import CreateAIExtractedUserBusinessModel
from app.models.ai_extracted_external_business_entity_model import CreateAIExtractedExternalBusinessModel
from app.models.ai_is_user_business_entity_recognized_model import CreateAIIsUserBusinessEntityRecognizedModel
from app.models.ai_is_external_business_entity_recognized_model import CreateAIIsExternalBusinessEntityRecognizedModel
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from abc import ABC, abstractmethod

class ExtractedInvoiceDataMenagerABC(ABC):

    @abstractmethod
    async def create_invoice_data(self, invoice_data: dict):
        ...

    @abstractmethod
    async def _create_ai_extracted_invoice(self, create_ai_extracted_invoice_model: CreateAIExtractedInvoiceModel, user_id: str, session: AsyncSession) -> AIExtractedInvoiceModel:
        ...

    @abstractmethod
    async def _create_ai_extracted_invoice_items(self, invoice_items: list[CreateAIExtractedInvoiceItemModel], user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        ...

    @abstractmethod
    async def _create_ai_extracted_user_business_entity(self, create_ai_extracted_user_business_entity: CreateAIExtractedUserBusinessModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        ...

    @abstractmethod
    async def _create_ai_extracted_external_business_entity(self, create_ai_extracted_external_business_entity: CreateAIExtractedExternalBusinessModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        ...

    @abstractmethod
    async def _create_ai_is_extracted_user_business_entity_recognized(self, create_ai_is_user_business_entity_recognized: CreateAIIsUserBusinessEntityRecognizedModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        ...

    @abstractmethod
    async def _create_ai_is_extracted_external_business_entity_recognized(self, create_ai_is_external_business_entity_recognized: CreateAIIsExternalBusinessEntityRecognizedModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        ...

    @abstractmethod
    async def try_to_recognize_user_business_entity_by_name(self, user_id: str, name: str, session: AsyncSession) -> list:
        ...
    
    @abstractmethod
    async def try_to_recognize_user_business_entity_by_nip(self, user_id: str, nip: str, session: AsyncSession) -> list:
        ...
    
    @abstractmethod
    async def try_to_recognize_external_business_entity_by_name(self, user_id: str, name: str, session: AsyncSession) -> list:
        ...

    @abstractmethod
    async def try_to_recognize_external_business_entity_by_nip(self, user_id: str, nip: str, session: AsyncSession) -> list:
        ...