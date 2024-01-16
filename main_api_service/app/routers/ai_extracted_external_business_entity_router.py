from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
from app.registries.get_repositories_registry import get_repositories_registry
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
    )
from app.models.ai_extracted_external_business_entity_model import (
    AIExtractedExternalBusinessModel,
    UpdateAIExtractedExternalBusinessModel
)
from app.models.ai_is_external_business_entity_recognized_model import UpdateAIIsExternalBusinessEntityRecognizedModel
from app.models.external_business_entity_model import (
    CreateExternalBusinessEntityModel,
    ExternalBusinessEntityModel
)
from app.schema.schema import (
    AIExtractedExternalBusinessEntity,
    ExternalBusinessEntity
)
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisJWTNotFoundError
)
from app.models.jwt_model import (
    JWTPayloadModel
)
from uuid import uuid4
from typing import List


router = APIRouter()
http_bearer = HTTPBearer()


@router.get("/ai-extracted-external-business-entity-module/get-ai-extracted-external-business-entity/")
async def get_ai_extracted_external_busines_entity(
    ai_extracted_invoice_id: str, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        ai_extracted_external_business_entity_postgres_repository = await repositories_registry.return_ai_extracted_external_business_entity_postgres_repository(postgres_session)
        

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extracted_external_business_entity: AIExtractedExternalBusinessEntity = await ai_extracted_external_business_entity_postgres_repository.get_extracted_external_business_entity(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        ai_extracted_external_business_entity_model: AIExtractedExternalBusinessModel = await AIExtractedExternalBusinessModel.ai_extracted_external_business_schema_to_model(
            extracted_external_business_entity_schema=ai_extracted_external_business_entity
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(ai_extracted_external_business_entity_model))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/ai-extracted-external-business-entity-module/update-ai-extracted-external-business-entity/")
async def update_ai_extracted_external_busines_entity(
    update_ai_extracted_external_busines_entity_model: UpdateAIExtractedExternalBusinessModel, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        ai_extracted_external_business_entity_postgres_repository = await repositories_registry.return_ai_extracted_external_business_entity_postgres_repository(postgres_session)
        

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await ai_extracted_external_business_entity_postgres_repository.update_extracted_external_business_entity(
            user_id=jwt_payload.id,
            update_ai_extracted_external_business_entity=update_ai_extracted_external_busines_entity_model
        )
        

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Extracted external business entity succesfully updated."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post("/ai-extracted-external-business-entity-module/accept-ai-extracted-external-business-entity/")
async def accept_ai_extracted_external_busines_entity(
    ai_extracted_invoice_id: str, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        ai_extracted_external_business_entity_postgres_repository = await repositories_registry.return_ai_extracted_external_business_entity_postgres_repository(postgres_session)
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        ai_is_external_business_entity_recognized_postgres_repository = await repositories_registry.return_ai_is_external_business_recognized_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extracted_external_business_entity: AIExtractedExternalBusinessEntity = await ai_extracted_external_business_entity_postgres_repository.get_extracted_external_business_entity(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        ai_extracted_external_business_entity_model: AIExtractedExternalBusinessModel = await AIExtractedExternalBusinessModel.ai_extracted_external_business_schema_to_model(
            extracted_external_business_entity_schema=ai_extracted_external_business_entity
        )

        create_extracted_external_business_entity_model: CreateExternalBusinessEntityModel(
            name=ai_extracted_external_business_entity_model.name,
            city=ai_extracted_external_business_entity_model.city,
            postal_code=ai_extracted_external_business_entity_model.postal_code,
            street=ai_extracted_external_business_entity_model.street,
            nip=ai_extracted_external_business_entity_model.nip
        )

        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.create_external_business_entity(
            user_id=jwt_payload.id,
            new_external_business_entity=create_extracted_external_business_entity_model
        )

        external_business_entity_model: ExternalBusinessEntityModel = await ExternalBusinessEntityModel.external_business_entity_schema_to_model(
            external_business_entity_schema=external_business_entity
        )

        update_ai_is_external_business_entity_recognized_model: UpdateAIIsExternalBusinessEntityRecognizedModel = UpdateAIIsExternalBusinessEntityRecognizedModel(
            extracted_invoice_id=ai_extracted_invoice_id,
            is_recognized=True,
            external_business_entity_id=external_business_entity_model.id
        )

        await ai_is_external_business_entity_recognized_postgres_repository.update_is_external_business_entity_recognized(
            user_id=jwt_payload.id,
            update_is_external_business_entity_recognized=update_ai_is_external_business_entity_recognized_model
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Extracted external business entity has been accepted."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))