from pydantic import BaseModel, ConfigDict
from typing import List
from typing import Optional
from app.models.invoice_item_model import CreateInvoiceItemModel, UpdateInvoiceItemModel

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
    notes: str
    is_settled: bool = False
    is_accepted: bool = True
    is_issued: bool = True
    invoice_item: List[CreateInvoiceItemModel]


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
                "is_settled": False,
                "is_accepted": True,
                "is_issued": True,
                "invoice_item": [
                    {
                        "ordinal_number": 1,
                        "item_description": "My product/service name",
                        "net_value": 8.00,
                        "gross_value": 10.00
                    }
                ]
                }
            }
        )
    id: str
    user_business_entity_id: Optional[str] = None
    external_business_entity_id: Optional[str] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[str] = None
    sale_date: Optional[str] = None
    payment_method: Optional[str] = None
    payment_deadline: Optional[str] = None
    notes: str
    is_settled: Optional[bool] = None
    is_accepted: Optional[bool] = None
    is_issued: Optional[bool] = None
    invoice_item: Optional[List[UpdateInvoiceItemModel]] = None