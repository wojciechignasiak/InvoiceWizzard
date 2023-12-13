from pydantic import BaseModel, ConfigDict
from typing import Optional

class CreateUserBusinessEntityModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "company_name": "Company Name",
                "city": "Warsaw",
                "postal_code": "00-000",
                "street": "ul. Nowa 3/4",
                "nip": "8386732400",
                }
            }
        )
    company_name: str
    city: Optional[str]
    postal_code: Optional[str]
    street: Optional[str]
    nip: str

class UpdateUserBusinessEntityModel(CreateUserBusinessEntityModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "a91031db-fc69-4b48-878e-0db79cef4cca",
                "company_name": "Company Name",
                "city": "Warsaw",
                "postal_code": "00-000",
                "street": "ul. Nowa 3/4",
                "nip": "8386732400",
                }
            }
        )
    id: str

class UserBusinessEntityModel(UpdateUserBusinessEntityModel):
    pass