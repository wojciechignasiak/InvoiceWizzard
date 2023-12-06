from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from app.database.get_repositories_registry import get_repositories_registry
from app.database.repositories_registry import RepositoriesRegistry
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError, 
    RedisJWTNotFoundError,
    RedisSetError,
    RedisNotFoundError
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
from app.models.external_business_entity_model import (
    CreateExternalBusinessEntityModel,
    UpdateExternalBusinessEntityModel,
    ExternalBusinessEntityModel
)
from app.schema.schema import ExternalBusinessEntity
import ast
from aiokafka import AIOKafkaProducer
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client
from app.kafka.events.user_business_entity_events import UserBusinessEntityEvents

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/external-business-entity-module/create-external-business-entity/", response_model=ExternalBusinessEntityModel)
async def create_external_business_entity(
    new_external_business_entity: CreateExternalBusinessEntityModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        is_unique: bool = await external_business_entity_postgres_repository.is_external_business_entity_unique(
            user_id=jwt_payload.id,
            new_external_business_entity=new_external_business_entity
        )

        if is_unique == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="External business entity with provided name/nip/krs arleady exists.")

        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.create_external_business_entity(
            user_id=jwt_payload.id, 
            new_external_business_entity=new_external_business_entity
            )
        
        external_business_entity_model = ExternalBusinessEntityModel(
            id=str(external_business_entity.id),
            company_name=external_business_entity.company_name,
            city=external_business_entity.city,
            postal_code=external_business_entity.postal_code,
            street=external_business_entity.street,
            nip=external_business_entity.nip,
            krs=external_business_entity.krs
        )
        
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=external_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/external-business-entity-module/get-external-business-entity/", response_model=ExternalBusinessEntityModel)
async def get_external_business_entity(
    external_business_entity_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.get_external_business_entity(
            user_id=jwt_payload.id,
            external_business_entity_id=external_business_entity_id
        )
        
        external_business_entity_model = ExternalBusinessEntityModel(
            id=str(user_business_entity.id),
            company_name=user_business_entity.company_name,
            city=user_business_entity.city,
            postal_code=user_business_entity.postal_code,
            street=user_business_entity.street,
            nip=user_business_entity.nip,
            krs=user_business_entity.krs
        )
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=external_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/external-business-entity-module/get-all-external-business-entities/")
async def get_all_external_business_entities(
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        external_business_entity_list: list = await external_business_entity_postgres_repository.get_all_external_business_entities(
            user_id=jwt_payload.id
        )
        external_business_entity_model_list = []
        for external_business_entity in external_business_entity_list:
            external_business_entity_model = ExternalBusinessEntityModel(
                id=str(external_business_entity.id),
                company_name=external_business_entity.company_name,
                city=external_business_entity.city,
                postal_code=external_business_entity.postal_code,
                street=external_business_entity.street,
                nip=external_business_entity.nip,
                krs=external_business_entity.krs
            )
            external_business_entity_model_list.append(external_business_entity_model.model_dump())
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=external_business_entity_model_list)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.patch("/external-business-entity-module/update-external-business-entity/", response_model=ExternalBusinessEntityModel)
async def update_external_business_entity(
    update_external_business_entity: UpdateExternalBusinessEntityModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        is_unique: bool = await external_business_entity_postgres_repository.is_external_business_entity_unique_beside_one_to_update(
            user_id=jwt_payload.id,
            update_external_business_entity=update_external_business_entity
        )

        if is_unique == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="External business entity with provided name/nip/krs arleady exists.")

        updated_external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.update_external_business_entity(
            user_id=jwt_payload.id,
            update_external_business_entity=update_external_business_entity
        )
        
        external_business_entity_model = ExternalBusinessEntityModel(
            id=str(updated_external_business_entity.id),
            company_name=updated_external_business_entity.company_name,
            city=updated_external_business_entity.city,
            postal_code=updated_external_business_entity.postal_code,
            street=updated_external_business_entity.street,
            nip=updated_external_business_entity.nip,
            krs=updated_external_business_entity.krs
        )
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=external_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    