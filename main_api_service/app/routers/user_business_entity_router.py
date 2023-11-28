from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from app.database.get_repositories_registry import get_repositories_registry
from app.database.repositories_registry import RepositoriesRegistry
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError, 
    RedisJWTNotFoundError
    )
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.session.get_session import get_session
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError, 
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError
    )
from app.models.jwt_model import (
    JWTPayloadModel
)
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel,
    UserBusinessEntityModel
)
from app.schema.schema import UserBusinessEntity

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/user-business-entity-module/create-user-business-entity/", response_model=UserBusinessEntityModel)
async def create_user_business_entity(
    new_user_business_entity: CreateUserBusinessEntityModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_business_entity_postgres_repository = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.create_user_business_entity(
            user_id=jwt_payload.id, 
            new_user_business_entity=new_user_business_entity
            )
        
        user_business_entity_model = UserBusinessEntityModel(
            id=str(user_business_entity.id),
            user_id=str(user_business_entity.user_id),
            company_name=user_business_entity.company_name,
            city=user_business_entity.city,
            postal_code=user_business_entity.postal_code,
            street=user_business_entity.street,
            nip=user_business_entity.nip,
            krs=user_business_entity.krs
        )
        
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=user_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.get("/user-business-entity-module/get-user-business-entity/", response_model=UserBusinessEntityModel)
async def get_user_business_entity(
    user_business_entity_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_business_entity_postgres_repository = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=user_business_entity_id
        )
        
        user_business_entity_model = UserBusinessEntityModel(
            id=str(user_business_entity.id),
            user_id=str(user_business_entity.user_id),
            company_name=user_business_entity.company_name,
            city=user_business_entity.city,
            postal_code=user_business_entity.postal_code,
            street=user_business_entity.street,
            nip=user_business_entity.nip,
            krs=user_business_entity.krs
        )
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=user_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))