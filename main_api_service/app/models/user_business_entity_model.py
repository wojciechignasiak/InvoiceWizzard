from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional

class CreateUserBusinessEntityModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "company_name": "Company Name",
                "city": "Warsaw",
                "postal_code": "00-000",
                "street": "ul. Nowa 3/4",
                "nip": "8386732400",
                "krs": "0123624482"
                }
            }
        )
    company_name: str
    city: Optional[str]
    postal_code: Optional[str]
    street: Optional[str]
    nip: Optional[str]
    krs: Optional[str]