from pydantic import BaseModel, Configdict
from datetime import date
from uuid import uuid4
from datetime import date
from app.schema.schema import AIExtractionFailure

class CreateAIExtractionFailureModel(BaseModel):

    user_id: str
    invoice_pdf: str

    @property
    def id(self):
        return uuid4()
    
    @property
    def date(self):
        return date.today()


class AIExtractionFailureModel(BaseModel):
    model_config = Configdict(json_schema_extra={
        "example":{
                "id": "cfafb4bd-59e0-46e5-9005-6afd7e5b8a38",
                "invoice_pdf": "file_location",
                "date": "2023-12-05",
                }
            }
        )
    id: str
    invoice_pdf: str
    date: date

    async def ai_extraction_failure_schema_to_model(
            ai_extraction_failure_schema: AIExtractionFailure
            ) -> "AIExtractionFailureModel":
        return AIExtractionFailureModel(
            id=str(ai_extraction_failure_schema.id),
            invoice_pdf=ai_extraction_failure_schema.invoice_pdf,
            date=ai_extraction_failure_schema.date,
        )