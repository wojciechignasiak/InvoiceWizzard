from pydantic import BaseModel, ConfigDict
from typing import Optional

class CreateInvoiceItemModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "ordinal_number": 1,
                "item_description": "My product/service name",
                "number_of_items": 1,
                "net_value": 8.00,
                "gross_value": 10.00
                }
            }
        )

    ordinal_number: int
    item_description: str
    number_of_items: int
    net_value: float
    gross_value: float

class UpdateInvoiceItemModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "d09ac12a-f128-4aa5-8b62-849ea61fcc3c",
                "invoice_id": "d09ac12a-f128-4aa5-8b62-849ea61fcc3c",
                "ordinal_number": 1,
                "item_description": "My product/service name",
                "number_of_items": 1,
                "net_value": 8.00,
                "gross_value": 10.00,
                }
            }
        )
    id: str
    invoice_id: str
    ordinal_number: Optional[int]
    item_description: Optional[str]
    number_of_items: Optional[int]
    net_value: Optional[float]
    gross_value: Optional[float]