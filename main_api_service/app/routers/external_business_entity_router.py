from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder
from app.registries.get_repositories_registry import get_repositories_registry
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError, 
    RedisJWTNotFoundError,
    RedisSetError,
    RedisNotFoundError
    )
from redis.asyncio import Redis
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
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel
)
from app.schema.schema import ExternalBusinessEntity
from typing import Optional

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/external-business-entity-module/create-external-business-entity/", response_model=ExternalBusinessEntityModel)
async def create_external_business_entity(
    new_external_business_entity: CreateExternalBusinessEntityModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_business_entity_postgres_repository = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
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
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="External business entity with provided name/nip arleady exists.")
        
        is_unique_in_user_business_entity: bool = await user_business_entity_postgres_repository.is_user_business_entity_unique(
            user_id=jwt_payload.id,
            new_user_business_entity=CreateUserBusinessEntityModel(
                company_name=new_external_business_entity.company_name,
                city=new_external_business_entity.city,
                postal_code=new_external_business_entity.postal_code,
                street=new_external_business_entity.street,
                nip=new_external_business_entity.nip
            )
        )
        
        if is_unique_in_user_business_entity == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="External business entity with provided name/nip arleady exists in User Business Entities.")
        
        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.create_external_business_entity(
            user_id=jwt_payload.id, 
            new_external_business_entity=new_external_business_entity
            )
        
        external_business_entity_model: ExternalBusinessEntityModel = ExternalBusinessEntityModel.external_business_entity_schema_to_model(external_business_entity)
        
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
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.get_external_business_entity(
            user_id=jwt_payload.id,
            external_business_entity_id=external_business_entity_id
        )
        
        external_business_entity_model: ExternalBusinessEntityModel = ExternalBusinessEntityModel.external_business_entity_schema_to_model(external_business_entity)
        
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
    page: int,
    items_per_page: int,
    company_name: Optional[str] = None,
    city: Optional[str] = None,
    postal_code: Optional[str] = None,
    street: Optional[str] = None,
    nip: Optional[str] = None,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
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
            user_id=jwt_payload.id,
            page=page,
            items_per_page=items_per_page,
            company_name=company_name,
            city=city,
            postal_code=postal_code,
            street=street,
            nip=nip
        )
        external_business_entities_model = []
        for external_business_entity in external_business_entity_list:
            external_business_entity_model: ExternalBusinessEntityModel = ExternalBusinessEntityModel.external_business_entity_schema_to_model(external_business_entity)
            external_business_entities_model.append(external_business_entity_model)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(external_business_entities_model))
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
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
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
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="External business entity with provided name/nip arleady exists.")

        updated_external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.update_external_business_entity(
            user_id=jwt_payload.id,
            update_external_business_entity=update_external_business_entity
        )
        
        external_business_entity_model: ExternalBusinessEntityModel = ExternalBusinessEntityModel.external_business_entity_schema_to_model(updated_external_business_entity)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=external_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.delete("/external-business-entity-module/remove-external-business-entity/")
async def remove_external_business_entity(
    external_business_entity_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        external_business_entity_postgres_repository = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        is_external_business_entity_removed = await external_business_entity_postgres_repository.remove_external_business_entity(
            user_id=jwt_payload.id,
            external_business_entity_id=external_business_entity_id
        )
        
        if is_external_business_entity_removed == False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="External business entity has not been removed.")
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "External business entity has been removed."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (PostgreSQLNotFoundError, RedisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))