from pydantic import BaseModel, ConfigDict
from typing import Optional
from pydantic.functional_validators import field_validator
from uuid import UUID, uuid4
from app.schema.schema import AIExtractedUserBusinessEntity

class CreateAIExtractedUserBusinessModel(BaseModel):
    company_name: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    nip: Optional[str] = None

    @property
    def id(self):
        return uuid4()
    
class UpdateAIExtractedUserBusinessModel(BaseModel):
    extracted_invoice_id: UUID
    company_name: str
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    nip: str

    @field_validator("extracted_invoice_id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value
    
class AIExtractedUserBusinessEntityModel(BaseModel):
    id: str
    extracted_invoice_id: str
    company_name: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    nip: Optional[str] = None

    async def ai_extracted_user_business_schema_to_model(
            extracted_user_business_entity_schema: AIExtractedUserBusinessEntity
            ) -> "AIExtractedUserBusinessEntityModel":
        return AIExtractedUserBusinessEntityModel(
            id=str(extracted_user_business_entity_schema.id),
            extracted_invoice_id=str(extracted_user_business_entity_schema.extracted_invoice_id),
            company_name=extracted_user_business_entity_schema.company_name,
            city=extracted_user_business_entity_schema.city,
            street=extracted_user_business_entity_schema.street,
            postal_code=extracted_user_business_entity_schema.postal_code,
            nip=extracted_user_business_entity_schema.nip
        )
