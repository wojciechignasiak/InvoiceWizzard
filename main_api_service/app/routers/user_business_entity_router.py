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
from app.models.user_business_entity_model import (
    CreateUserBusinessEntityModel,
    UpdateUserBusinessEntityModel,
    UserBusinessEntityModel
)
from app.types.postgres_repository_abstract_types import (
    UserBusinessEntityPostgresRepositoryABC,
    ExternalBusinessEntityPostgresRepositoryABC,
    InvoicePostgresRepositoryABC
)
from app.types.redis_repository_abstract_types import (
    UserRedisRepositoryABC,
    UserBusinessEntityRedisRepositoryABC
)
from app.types.kafka_event_abstract_types import (
    UserBusinessEntityEventsABC
)
from app.models.external_business_entity_model import CreateExternalBusinessEntityModel
from app.schema.schema import UserBusinessEntity
from uuid import uuid4
import ast
from aiokafka import AIOKafkaProducer
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client
from app.registries.events_registry_abc import EventsRegistryABC
from app.registries.get_events_registry import get_events_registry
from typing import Optional

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/user-business-entity-module/create-user-business-entity/", response_model=UserBusinessEntityModel)
async def create_user_business_entity(
    new_user_business_entity: CreateUserBusinessEntityModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        is_unique: bool = await user_business_entity_postgres_repository.is_user_business_entity_unique(
            user_id=jwt_payload.id,
            new_user_business_entity=new_user_business_entity
        )
        
        if is_unique == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User business entity with provided company name/nip arleady exists.")

        is_unique_in_external_business_entity: bool = await external_business_entity_postgres_repository.is_external_business_entity_unique(
            user_id=jwt_payload.id,
            new_external_business_entity=CreateExternalBusinessEntityModel(
                name=new_user_business_entity.company_name,
                city=new_user_business_entity.city,
                postal_code=new_user_business_entity.postal_code,
                street=new_user_business_entity.street,
                nip=new_user_business_entity.nip
            )
        )
        
        if is_unique_in_external_business_entity == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User business entity with provided name/nip arleady exists in External Business Entities.")

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.create_user_business_entity(
            user_id=jwt_payload.id, 
            new_user_business_entity=new_user_business_entity
            )
        
        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)

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
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=user_business_entity_id
        )
        
        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=user_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/user-business-entity-module/get-all-user-business-entities/")
async def get_all_user_business_entities(
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
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entities: list = await user_business_entity_postgres_repository.get_all_user_business_entities(
            user_id=jwt_payload.id,
            page=page,
            items_per_page=items_per_page,
            company_name=company_name,
            city=city,
            postal_code=postal_code,
            street=street,
            nip=nip
        )
        user_business_entities_model = [await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity) for user_business_entity in user_business_entities]
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(user_business_entities_model))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.patch("/user-business-entity-module/update-user-business-entity/", response_model=UserBusinessEntityModel)
async def update_user_business_entity(
    update_user_business_entity: UpdateUserBusinessEntityModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        is_unique: bool = await user_business_entity_postgres_repository.is_user_business_entity_unique_beside_one_to_update(
            user_id=jwt_payload.id,
            update_user_business_entity=update_user_business_entity
        )

        if is_unique == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User business entity with provided name/nip arleady exists.")

        updated_user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.update_user_business_entity(
            user_id=jwt_payload.id,
            update_user_business_entity=update_user_business_entity
        )
        
        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(updated_user_business_entity)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=user_business_entity_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.put("/user-business-entity-module/initialize-user-business-entity-removal/")
async def initialize_user_business_entity_removal(
    user_business_entity_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):
    try:
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        user_business_entity_redis_repository: UserBusinessEntityRedisRepositoryABC = await repositories_registry.return_user_business_entity_redis_repository(redis_client)
        user_business_entity_events: UserBusinessEntityEventsABC = await events_registry.return_user_business_events(kafka_producer_client)
        
        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=user_business_entity_id
        )
        
        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)

        number_of_invoices: int = await invoice_postgres_repository.count_invoices_related_to_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=user_business_entity_model.id
        )

        if number_of_invoices != 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"There are {number_of_invoices} invoices related to the user business entity. Remove them first.")
        
        key_id = str(uuid4())

        await user_business_entity_redis_repository.initialize_user_business_entity_removal(
            key_id=key_id,
            user_business_entity_id=user_business_entity_id
            )
        
        await user_business_entity_events.remove_user_business_entity(
            id=key_id,
            email_address=jwt_payload.email,
            user_business_entity_name=user_business_entity.company_name
            )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "User business entity removal process has been initialized. Check your email address."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.delete("/user-business-entity-module/confirm-user-business-entity-removal/")
async def confirm_user_business_entity_removal(
    id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):

    try:
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        user_business_entity_redis_repository: UserBusinessEntityRedisRepositoryABC = await repositories_registry.return_user_business_entity_redis_repository(redis_client)
        user_business_entity_events: UserBusinessEntityEventsABC = await events_registry.return_user_business_events(kafka_producer_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        user_business_entity_id: bytes = await user_business_entity_redis_repository.retrieve_user_business_entity_removal(
            key_id=id
        )

        user_business_entity_id = user_business_entity_id.decode()
        user_business_entity_id = ast.literal_eval(user_business_entity_id)
        user_business_entity_id = user_business_entity_id["id"]

        user_business_entity = await user_business_entity_postgres_repository.get_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=user_business_entity_id
        )

        number_of_invoices: int = await invoice_postgres_repository.count_invoices_related_to_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=user_business_entity_id
        )

        if not number_of_invoices:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"There are {number_of_invoices} invoices related to the user business entity. Remove them first.")

        is_user_business_entity_removed = await user_business_entity_postgres_repository.remove_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=user_business_entity_id
        )
        
        if is_user_business_entity_removed == False:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User business entity has not been removed.")
        
        await user_business_entity_redis_repository.delete_user_business_entity_removal(
            key_id=id
        )

        await user_business_entity_events.user_business_entity_removed(
            email_address=jwt_payload.email,
            user_business_entity_name=user_business_entity.company_name
        )
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "User business entity has been removed."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (PostgreSQLNotFoundError, RedisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))