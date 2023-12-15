from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schema.schema import ExternalBusinessEntity

class CreateExternalBusinessEntityModel(BaseModel):
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

class UpdateExternalBusinessEntityModel(CreateExternalBusinessEntityModel):
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

class ExternalBusinessEntityModel(UpdateExternalBusinessEntityModel):
    pass

    def external_business_entity_schema_to_model(external_business_entity_schema: ExternalBusinessEntity) -> "ExternalBusinessEntityModel":
        return ExternalBusinessEntityModel(
            id=str(external_business_entity_schema.id),
            company_name=external_business_entity_schema.company_name,
            city=external_business_entity_schema.city,
            postal_code=external_business_entity_schema.postal_code,
            street=external_business_entity_schema.street,
            nip=external_business_entity_schema.nip
        )