from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional
from app.schema.schema import Invoice
from uuid import UUID, uuid4
from pydantic.functional_validators import field_validator

class CreateInvoiceModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "user_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "external_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "invoice_number": "1/2023",
                "issue_date": "2023-12-05",
                "sale_date": "2023-12-05",
                "payment_method": "Card",
                "payment_deadline": "2023-12-10",
                "notes": "This is an example Invoice",
                "is_settled": False,
                "is_accepted": True,
                "is_issued": True,
                }
            }
        )
    
    user_business_entity_id: UUID
    external_business_entity_id: UUID
    invoice_number: str
    issue_date: date
    sale_date: date
    payment_method: str
    payment_deadline: date
    notes: str
    is_settled: bool = False
    is_accepted: bool = True
    is_issued: bool = True

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


class UpdateInvoiceModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "cfafb4bd-59e0-46e5-9005-6afd7e5b8a38",
                "user_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "external_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "invoice_number": "1/2023",
                "issue_date": "2023-12-05",
                "sale_date": "2023-12-05",
                "payment_method": "Card",
                "payment_deadline": "2023-12-10",
                "notes": "This is an example Invoice",
                "is_settled": False,
                "is_accepted": True,
                "is_issued": True
                }
            }
        )
    id: UUID
    user_business_entity_id: Optional[UUID] = None
    external_business_entity_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[date] = None
    sale_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_deadline: Optional[date] = None
    notes: str
    is_settled: Optional[bool] = None
    is_accepted: Optional[bool] = None
    is_issued: Optional[bool] = None

    @field_validator("id", "user_business_entity_id", "external_business_entity_id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value
    
    @field_validator("sale_date", "issue_date", "payment_deadline")
    def parse_sale_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
        return value



class InvoiceModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "cfafb4bd-59e0-46e5-9005-6afd7e5b8a38",
                "user_id": "cdee4370-dfd5-416e-821e-054693ae4de5",
                "user_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "external_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "invoice_number": "1/2023",
                "issue_date": "2023-12-05",
                "sale_date": "2023-12-05",
                "payment_method": "Card",
                "payment_deadline": "2023-12-10",
                "notes": "This is an example Invoice",
                "is_settled": False,
                "is_accepted": True,
                "is_issued": True
                }
            }
        )
    id: str
    user_id: str
    user_business_entity_id: str
    external_business_entity_id: str
    invoice_pdf: Optional[str] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[str] = None
    sale_date: Optional[str] = None
    added_date: Optional[str] = None
    payment_method: Optional[str] = None
    payment_deadline: Optional[str] = None
    notes: Optional[str] = None
    is_settled: Optional[bool] = None
    is_accepted: Optional[bool] = None
    is_issued: Optional[bool] = None

    def invoice_schema_to_model(invoice_schema: Invoice) -> "InvoiceModel":
        return InvoiceModel(
            id=str(invoice_schema.id),
            user_id=str(invoice_schema.user_id),
            user_business_entity_id=str(invoice_schema.user_business_entity_id),
            external_business_entity_id=str(invoice_schema.external_business_entity_id),
            invoice_pdf=invoice_schema.invoice_pdf,
            invoice_number=invoice_schema.invoice_number,
            issue_date=str(invoice_schema.issue_date) if invoice_schema.issue_date else None,
            sale_date=str(invoice_schema.sale_date) if invoice_schema.sale_date else None,
            added_date=str(invoice_schema.added_date) if invoice_schema.added_date else None,
            payment_method=invoice_schema.payment_method,
            payment_deadline=str(invoice_schema.payment_deadline) if invoice_schema.payment_deadline else None,
            notes=invoice_schema.notes,
            is_settled=invoice_schema.is_settled,
            is_accepted=invoice_schema.is_accepted,
            is_issued=invoice_schema.is_issued
        )