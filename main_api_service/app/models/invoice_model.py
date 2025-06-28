from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional

from uuid import UUID, uuid4
from pydantic.functional_validators import field_validator
from main_api_service.app.models.user_business_entity_model import UserBusinessEntityModel
from main_api_service.app.models.external_business_entity_model import ExternalBusinessEntityModel

class CreateInvoiceItemModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
                "item_description": "My product/service name",
                "number_of_items": 1,
                "net_value": 8.00,
                "gross_value": 10.00,
            }
        }
    )
    item_description: str
    number_of_items: int
    net_value: float
    gross_value: float

    @property
    def id(self):
        return uuid4()

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
    notes: Optional[str] = None
    is_settled: bool
    is_issued: bool
    invoice_items: list[CreateInvoiceItemModel]
    
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
                "is_issued": True
                }
            }
        )
    id: UUID
    user_business_entity_id: UUID
    external_business_entity_id: UUID
    invoice_number: str
    issue_date: date
    sale_date: date
    payment_method: str
    payment_deadline: date
    notes: str | None = None
    is_settled: bool
    is_issued: bool

class InvoiceItemModel(BaseModel):
    id: UUID
    invoice_id: UUID
    item_description: str
    number_of_items: int
    net_value: float
    gross_value: float
    in_trash: bool


class InvoiceModel(BaseModel):
    id: UUID
    user_business_entity: UserBusinessEntityModel
    external_business_entity: ExternalBusinessEntityModel
    invoice_pdf: str | None = None
    invoice_number: str
    issue_date: date
    sale_date: date
    added_date: date
    payment_method: str
    payment_deadline: date
    notes: Optional[str] = None
    is_settled: bool
    is_issued: bool
    in_trash: bool
    sum_gross_value: Optional[float] = None
    sum_net_value: Optional[float] = None
    invoice_items: tuple[InvoiceItemModel] | None = None
