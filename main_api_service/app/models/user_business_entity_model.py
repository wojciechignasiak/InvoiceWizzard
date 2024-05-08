from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schema.schema import UserBusinessEntity
from uuid import uuid4

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
    city: Optional[str] = None
    postal_code: Optional[str] = None
    street: Optional[str] = None
    nip: str

    @property
    def id(self):
        return uuid4()

class UpdateUserBusinessEntityModel(BaseModel):
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
    company_name: str
    city: Optional[str] = None
    postal_code: Optional[str] = None
    street: Optional[str] = None
    nip: str

class UserBusinessEntityModel(UpdateUserBusinessEntityModel):

    async def user_business_entity_schema_to_model(user_business_entity_schema: UserBusinessEntity) -> "UserBusinessEntityModel":
        return UserBusinessEntityModel(
            id=str(user_business_entity_schema.id),
            company_name=user_business_entity_schema.company_name,
            city=user_business_entity_schema.city,
            postal_code=user_business_entity_schema.postal_code,
            street=user_business_entity_schema.street,
            nip=user_business_entity_schema.nip
        )