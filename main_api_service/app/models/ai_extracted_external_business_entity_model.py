from pydantic import BaseModel, Configdict
from datetime import date
from typing import Optional
from pydantic.functional_validators import field_validator
from uuid import UUID, uuid4
from app.schema.schema import AIExtractedExternalBusinessEntity

class CreateAIExtractedExternalBusinessModel(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    nip: Optional[str] = None

    @property
    def id(self):
        return uuid4()
    
class UpdateAIExtractedExternalBusinessModel(BaseModel):
    extracted_invoice_id: UUID
    name: str
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    nip: Optional[str] = None

    @field_validator("extracted_invoice_id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value
    
class AIExtractedExternalBusinessModel(BaseModel):
    id: str
    extracted_invoice_id: str
    name: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    nip: Optional[str] = None

    async def ai_extracted_external_business_schema_to_model(
            extracted_external_business_entity_schema: AIExtractedExternalBusinessEntity
            ) -> "AIExtractedExternalBusinessModel":
        return AIExtractedExternalBusinessModel(
            id=str(extracted_external_business_entity_schema.id),
            extracted_invoice_id=str(extracted_external_business_entity_schema.extracted_invoice_id),
            name=extracted_external_business_entity_schema.name,
            city=extracted_external_business_entity_schema.city,
            street=extracted_external_business_entity_schema.street,
            postal_code=extracted_external_business_entity_schema.postal_code,
            nip=extracted_external_business_entity_schema.nip
        )