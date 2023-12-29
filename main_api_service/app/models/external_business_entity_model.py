from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schema.schema import ExternalBusinessEntity
from uuid import uuid4

class CreateExternalBusinessEntityModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "name": "Name/Company Name",
                "city": "Warsaw",
                "postal_code": "00-000",
                "street": "ul. Nowa 3/4",
                "nip": "8386732400",
                }
            }
        )
    name: str
    city: Optional[str]
    postal_code: Optional[str]
    street: Optional[str]
    nip: Optional[str]

    @property
    def id(self):
        return uuid4()

class UpdateExternalBusinessEntityModel(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example":{
                "id": "a91031db-fc69-4b48-878e-0db79cef4cca",
                "name": "Name/Company Name",
                "city": "Warsaw",
                "postal_code": "00-000",
                "street": "ul. Nowa 3/4",
                "nip": "8386732400",
                }
            }
        )
    id: str
    name: str
    city: Optional[str]
    postal_code: Optional[str]
    street: Optional[str]
    nip: Optional[str]

class ExternalBusinessEntityModel(UpdateExternalBusinessEntityModel):
    pass

    async def external_business_entity_schema_to_model(external_business_entity_schema: ExternalBusinessEntity) -> "ExternalBusinessEntityModel":
        return ExternalBusinessEntityModel(
            id=str(external_business_entity_schema.id),
            name=external_business_entity_schema.name,
            city=external_business_entity_schema.city,
            postal_code=external_business_entity_schema.postal_code,
            street=external_business_entity_schema.street,
            nip=external_business_entity_schema.nip
        )