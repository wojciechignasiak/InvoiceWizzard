from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID, uuid4
from app.schema.schema import InvoiceItem
from pydantic.functional_validators import field_validator

class CreateInvoiceItemModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "item_description": "My product/service name",
                "number_of_items": 1,
                "net_value": 8.00,
                "gross_value": 10.00
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


class InvoiceItemModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "d09ac12a-f128-4aa5-8b62-849ea61fcc3c",
                "invoice_id": "d09ac12a-f128-4aa5-8b62-849ea61fcc3c",
                "item_description": "My product/service name",
                "number_of_items": 1,
                "net_value": 8.00,
                "gross_value": 10.00,
                "in_trash": False
                }
            }
        )
    id: str
    invoice_id: str
    item_description: str
    number_of_items: int
    net_value: float
    gross_value: float
    in_trash: bool

    @property
    def vat_percent(self):
        return ((self.gross_value - self.net_value) / self.net_value) * 100
    
    def invoice_item_schema_to_model(invoice_item_schema: InvoiceItem) -> "InvoiceItemModel":
        return InvoiceItemModel(
            id=str(invoice_item_schema.id),
            invoice_id=str(invoice_item_schema.invoice_id),
            item_description=invoice_item_schema.item_description,
            number_of_items=invoice_item_schema.number_of_items,
            net_value=invoice_item_schema.net_value,
            gross_value=invoice_item_schema.gross_value
        )

class UpdateInvoiceItemModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "d09ac12a-f128-4aa5-8b62-849ea61fcc3c",
                "invoice_id": "d09ac12a-f128-4aa5-8b62-849ea61fcc3c",
                "item_description": "My product/service name",
                "number_of_items": 1,
                "net_value": 8.00,
                "gross_value": 10.00,
                }
            }
        )
    id: UUID
    invoice_id: UUID
    item_description: Optional[str]
    number_of_items: Optional[int]
    net_value: Optional[float]
    gross_value: Optional[float]

    @field_validator("id", "invoice_id")
    def parse_id(cls, value):
        if isinstance(value, str):
            return UUID(value)
        return value