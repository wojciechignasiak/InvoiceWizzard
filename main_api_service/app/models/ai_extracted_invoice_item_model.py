from pydantic import BaseModel, Configdict
from datetime import date
from typing import Optional
from pydantic.functional_validators import field_validator
from uuid import UUID, uuid4
from app.schema.schema import AIExtractedInvoiceItem

class CreateAIExtractedInvoiceItemModel(BaseModel):
    item_description: Optional[str] = None
    number_of_items: Optional[int] = None
    net_value: Optional[float] = None
    gross_value: Optional[float] = None

    @property
    def id(self):
        return uuid4()
    
class CreateManuallyAIExtractedInvoiceItemModel(BaseModel):
    extracted_invoice_id: UUID
    item_description: str
    number_of_items: int
    net_value: float
    gross_value: float

class UpdateAIExtractedInvoiceItemModel(BaseModel):
    id: UUID
    extracted_invoice_id: UUID
    item_description: str
    number_of_items: int
    net_value: float
    gross_value: float

    @field_validator("id","extracted_invoice_id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value
    

class AIExtractedInvoiceItemModel(BaseModel):
    id: str
    extracted_invoice_id: str
    item_description: Optional[str] = None
    number_of_items: Optional[int] = None
    net_value: Optional[float] = None
    gross_value: Optional[float] = None

    async def ai_extracted_invoice_item_schema_to_model(
            extracted_invoice_item_schema: AIExtractedInvoiceItem
            ) -> "AIExtractedInvoiceItemModel":
        return AIExtractedInvoiceItemModel(
            id=str(extracted_invoice_item_schema.id),
            extracted_invoice_id=str(extracted_invoice_item_schema.extracted_invoice_id),
            item_description=extracted_invoice_item_schema.item_description,
            number_of_items=extracted_invoice_item_schema.number_of_items,
            net_value=extracted_invoice_item_schema.net_value,
            gross_value=extracted_invoice_item_schema.gross_value
        )