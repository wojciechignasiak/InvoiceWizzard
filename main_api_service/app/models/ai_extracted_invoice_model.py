from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from pydantic.functional_validators import field_validator
from uuid import UUID, uuid4
from datetime import datetime, date
from app.schema.schema import AIExtractedInvoice

class CreateAIExtractedInvoiceModel(BaseModel):
    invoice_number: str
    issue_date: Optional[date] = None
    sale_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_deadline: Optional[date] = None
    notes: Optional[str] = None
    invoice_pdf: str
    is_issued: Optional[bool] = None
    

    @property
    def id(self):
        return uuid4()
    
    @property
    def added_date(self):
        return date.today()
    
    @field_validator("sale_date", "issue_date", "payment_deadline")
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value

class UpdateAIExtractedInvoiceModel(BaseModel):
    id: UUID
    invoice_number: str
    issue_date: date
    sale_date: date
    payment_method: str
    payment_deadline: date
    notes: Optional[str] = None
    is_issued: bool

    @field_validator("id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value
    
    @field_validator("sale_date", "issue_date", "payment_deadline")
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value

class AIExtractedInvoiceModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "cfafb4bd-59e0-46e5-9005-6afd7e5b8a38",
                "invoice_number": "1/2023",
                "issue_date": "2023-12-05",
                "sale_date": "2023-12-05",
                "payment_method": "Card",
                "payment_deadline": "2023-12-10",
                "notes": "This is an example Invoice",
                "is_settled": False,
                "is_issued": True,
                }
            }
        )
    id: str
    invoice_number: Optional[str] = None
    issue_date: Optional[date] = None
    sale_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_deadline: Optional[date] = None
    notes: Optional[str] = None
    invoice_pdf: str
    is_issued: Optional[bool] = None

    async def ai_extracted_invoice_schema_to_model(
            extracted_invoice_schema: AIExtractedInvoice
            ) -> "AIExtractedInvoiceModel":
        return AIExtractedInvoiceModel(
            id=str(extracted_invoice_schema.id),
            invoice_number=extracted_invoice_schema.invoice_number,
            issue_date=extracted_invoice_schema.issue_date,
            sale_date=extracted_invoice_schema.sale_date,
            payment_method=extracted_invoice_schema.payment_method,
            payment_deadline=extracted_invoice_schema.payment_deadline,
            notes=extracted_invoice_schema.notes,
            invoice_pdf=extracted_invoice_schema.invoice_pdf,
            is_issued=extracted_invoice_schema.is_issued
        )