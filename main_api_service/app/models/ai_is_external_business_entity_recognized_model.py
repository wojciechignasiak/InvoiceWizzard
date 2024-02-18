from pydantic import BaseModel, Configdict
from typing import Optional
from pydantic.functional_validators import field_validator
from uuid import UUID, uuid4
from app.schema.schema import AIIsExternalBusinessEntityRecognized

class CreateAIIsExternalBusinessEntityRecognizedModel(BaseModel):
    is_recognized: bool
    external_business_entity_id: Optional[str] = None

    @property
    def id(self):
        return uuid4()
    
class UpdateAIIsExternalBusinessEntityRecognizedModel(BaseModel):
    extracted_invoice_id: UUID
    is_recognized: bool
    external_business_entity_id: UUID

    @field_validator("extracted_invoice_id", "external_business_entity_id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value
    
class AIIsExternalBusinessEntityRecognizedModel(BaseModel):
    id: str
    extracted_invoice_id: str
    is_recognized: bool
    external_business_entity_id: Optional[str] = None

    async def ai_is_external_business_entity_recognized_schema_to_model(
            is_external_business_entity_recognized_schema: AIIsExternalBusinessEntityRecognized
            ) -> "AIIsExternalBusinessEntityRecognizedModel":
        
        return AIIsExternalBusinessEntityRecognizedModel(
            id=str(is_external_business_entity_recognized_schema.id),
            extracted_invoice_id=str(is_external_business_entity_recognized_schema.extracted_invoice_id),
            is_recognized=is_external_business_entity_recognized_schema.is_recognized,
            external_business_entity_id=str(is_external_business_entity_recognized_schema.external_business_entity_id)
        )