from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List
from app.models.ai_extracted_invoice_model import CreateAIExtractedInvoiceModel
from app.models.ai_extracted_invoice_item_model import CreateAIExtractedInvoiceItemModel
from app.models.ai_extracted_user_business_entity_model import CreateAIExtractedUserBusinessModel
from app.models.ai_extracted_external_business_entity_model import CreateAIExtractedExternalBusinessModel

class AIExtractedDataModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "user_id": "some_id",
                "invoice":
                    {
                    "invoice_number": "12/2023",
                    "issue_date": "2023-12-05",
                    "sale_date": "2023-12-05",
                    "payment_method": "Card",
                    "payment_deadline": "2023-12-10",
                    "notes": "This is an example Invoice",
                    "invoice_pdf": "invoice-ai/some_id/some_id/invoice.pdf",
                    "is_issued": False
                    },
                "invoice_items": [
                        {
                            "item_description": "My product/service name",
                            "number_of_items": 1,
                            "net_value": 8.00,
                            "gross_value": 10.00
                        },
                        {
                            "item_description": "My product/service name2",
                            "number_of_items": 2,
                            "net_value": 10.00,
                            "gross_value": 12.00
                        }
                    ],
                "user_business_entity":
                    {
                        "company_name": "Company Name",
                        "city": "Warsaw",
                        "postal_code": "00-000",
                        "street": "ul. Nowa 3/4",
                        "nip": "8386732400"
                    },
                "external_business_entity":
                    {
                        "name": "Name/Company Name",
                        "city": "Warsaw",
                        "postal_code": "00-000",
                        "street": "ul. Nowa 3/4",
                        "nip": "8386732400"
                    }
                }
            }
        )
    user_id: str
    invoice: CreateAIExtractedInvoiceModel
    invoice_items: List[CreateAIExtractedInvoiceItemModel]
    user_business_entity: CreateAIExtractedUserBusinessModel
    external_business_entity: CreateAIExtractedExternalBusinessModel