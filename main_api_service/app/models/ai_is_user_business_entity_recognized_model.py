from pydantic import BaseModel, Configdict
from typing import Optional
from pydantic.functional_validators import field_validator
from uuid import UUID, uuid4
from app.schema.schema import AIIsUserBusinessEntityRecognized

class CreateAIIsUserBusinessEntityRecognizedModel(BaseModel):
    is_recognized: bool
    user_business_entity_id: Optional[str] = None

    @property
    def id(self):
        return uuid4()
    
class UpdateAIIsUserBusinessEntityRecognizedModel(BaseModel):
    extracted_invoice_id: UUID
    is_recognized: bool
    user_business_entity_id: Optional[UUID] = None

    @field_validator("extracted_invoice_id", "user_business_entity_id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value
    
class AIIsUserBusinessEntityRecognizedModel(BaseModel):
    id: str
    extracted_invoice_id: str
    is_recognized: bool
    user_business_entity_id: Optional[str] = None

    async def ai_is_user_business_entity_recognized_schema_to_model(
            is_user_business_entity_recognized_schema: AIIsUserBusinessEntityRecognized
            ) -> "AIIsUserBusinessEntityRecognizedModel":
        return AIIsUserBusinessEntityRecognizedModel(
            id=str(is_user_business_entity_recognized_schema.id),
            extracted_invoice_id=str(is_user_business_entity_recognized_schema.extracted_invoice_id),
            is_recognized=is_user_business_entity_recognized_schema.is_recognized,
            user_business_entity_id=str(is_user_business_entity_recognized_schema.user_business_entity_id)
        )
