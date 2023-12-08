from pydantic import BaseModel, ConfigDict
from typing import List
from decimal import Decimal

class CreateInvoiceItemModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "ordinal_number": 1,
                "item_description": "My product/service name",
                "net_value": 8.00,
                "gross_value": 10.00,
                "tax_percentage": 0.20
                }
            }
        )

    ordinal_number: int
    item_description: str
    net_value: float
    gross_value: float
    tax_percent: Decimal

class CreateInvoiceManuallyModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "user_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "external_business_entity_id": "abcac67f-6d59-41b5-bf88-58fbaefbd725",
                "invoice_number": "1/2023",
                "issue_date": "2023-12-05",
                "sale_date": "2023-12-05",
                "payment_method": "Card",
                "payment_deadline": "2023-12-10",
                "is_settled": False,
                "is_accepted": True,
                "is_issued": True,
                "invoice_item": [
                    {
                        "ordinal_number": 1,
                        "item_description": "My product/service name",
                        "net_value": 8.00,
                        "gross_value": 10.00,
                        "tax_percentage": "20%"
                    }
                ]
                }
            }
        )
    
    user_business_entity_id: str
    external_business_entity_id: str
    invoice_number: str
    issue_date: str
    sale_date: str
    payment_method: str
    payment_deadline: str
    is_settled: bool = False
    is_accepted: bool = True
    is_issued: bool = True
    invoice_item: List[CreateInvoiceItemModel]