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
from app.models.ai_is_user_business_entity_recognized_model import (
    AIIsUserBusinessEntityRecognizedModel,
    UpdateAIIsUserBusinessEntityRecognizedModel
)
from app.models.ai_is_user_business_entity_recognized_model import UpdateAIIsUserBusinessEntityRecognizedModel
from app.schema.schema import (
    AIIsUserBusinessEntityRecognized,
)
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisJWTNotFoundError
)
from app.models.jwt_model import (
    JWTPayloadModel
)

router = APIRouter()
http_bearer = HTTPBearer()


@router.get("/ai-is-user-business-entity-recognized-module/get-ai-is-user-business-entity-recognized/")
async def get_ai_is_user_business_entity_recognized(
    ai_extracted_invoice_id: str, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        ai_is_user_business_entity_recognized_postgres_repository = await repositories_registry.return_ai_is_user_business_recognized_postgres_repository(postgres_session)
        

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_is_user_business_entity_recognized: AIIsUserBusinessEntityRecognized = await ai_is_user_business_entity_recognized_postgres_repository.get_is_user_business_recognized(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        ai_is_user_business_entity_recognized_model: AIIsUserBusinessEntityRecognizedModel = await AIIsUserBusinessEntityRecognizedModel.ai_is_user_business_entity_recognized_schema_to_model(
            is_user_business_entity_recognized_schema=ai_is_user_business_entity_recognized
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(ai_is_user_business_entity_recognized_model))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/ai-is-user-business-entity-recognized-module/update-ai-is-user-business-entity-recognized/")
async def update_ai_is_extracted_user_busines_entity_recognized(
    update_ai_is_user_business_entity_recognized_model: UpdateAIIsUserBusinessEntityRecognizedModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        ai_is_user_business_entity_recognized_postgres_repository = await repositories_registry.return_ai_is_user_business_recognized_postgres_repository(postgres_session)
        user_business_postgres_repository = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        if update_ai_is_user_business_entity_recognized_model.is_recognized == True & update_ai_is_user_business_entity_recognized_model.user_business_entity_id == None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User business entity id is required if you want to set is_recognized value to True")

        if update_ai_is_user_business_entity_recognized_model.user_business_entity_id != None:
            await user_business_postgres_repository.get_user_business_entity(
                user_id=jwt_payload.id,
                user_business_entity_id=update_ai_is_user_business_entity_recognized_model.user_business_entity_id,
            )


        await ai_is_user_business_entity_recognized_postgres_repository.update_is_user_business_recognized(
            user_id=jwt_payload.id,
            update_ai_is_user_business_entity_recognized=update_ai_is_user_business_entity_recognized_model
        )
        

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Is user business entity recognized succesfully updated."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))