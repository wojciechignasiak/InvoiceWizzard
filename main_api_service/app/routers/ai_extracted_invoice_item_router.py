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
from app.models.ai_extracted_invoice_item_model import (
    AIExtractedInvoiceItemModel, 
    UpdateAIExtractedInvoiceItemModel,
    CreateAIExtractedInvoiceItemModel,
    CreateManuallyAIExtractedInvoiceItemModel
)
from app.schema.schema import AIExtractedInvoiceItem
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisJWTNotFoundError
)
from app.types.postgres_repository_abstract_types import (
    AIExtractedInvoiceItemPostgresRepositoryABC
)
from app.types.redis_repository_abstract_types import (
    UserRedisRepositoryABC,
)
from app.types.kafka_event_abstract_types import (
    AIInvoiceEventsABC
)
from app.models.jwt_model import (
    JWTPayloadModel
)



router = APIRouter()
http_bearer = HTTPBearer()


@router.get("/ai-extracted-invoice-item-module/get-ai-extracted-invoice-items-by-ai-extracted-invoice-id/")
async def get_ai_extracted_invoice_items_by_ai_extracted_invoice_id(
    ai_extracted_invoice_id: str, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        extracted_invoice_items: list[AIExtractedInvoiceItem] = await ai_extracted_invoice_item_postgres_repository.get_all_extracted_invoice_item_data_by_extracted_invoice_id(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        invoice_item_models: list[AIExtractedInvoiceItemModel] = []

        for invoice_item in extracted_invoice_items:
            invoice_item_model: AIExtractedInvoiceItemModel = await AIExtractedInvoiceItemModel.ai_extracted_invoice_item_schema_to_model(
                extracted_invoice_item_schema=invoice_item
            )
            invoice_item_models.append(invoice_item_model)

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(invoice_item_models))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.patch("/ai-extracted-invoice-item-module/update-ai-extracted-invoice-item/")
async def update_ai_extracted_invoice_item(
    update_ai_extracted_invoice_item: UpdateAIExtractedInvoiceItemModel, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await ai_extracted_invoice_item_postgres_repository.update_extracted_invoice_item(
            user_id=jwt_payload.id,
            update_ai_extracted_invoice_item=update_ai_extracted_invoice_item
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Extracted invoice item has been updated successfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/ai-extracted-invoice-item-module/create-ai-extracted-invoice-item/")
async def create_ai_extracted_invoice_item(
    create_manually_ai_extracted_invoice_item: CreateManuallyAIExtractedInvoiceItemModel, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        create_ai_extracted_invoice_item: CreateAIExtractedInvoiceItemModel = CreateAIExtractedInvoiceItemModel(
            item_description=create_manually_ai_extracted_invoice_item.item_description,
            number_of_items=create_manually_ai_extracted_invoice_item.number_of_items,
            net_value=create_manually_ai_extracted_invoice_item.net_value,
            gross_value=create_manually_ai_extracted_invoice_item.gross_value
        )

        ai_extracted_invoice_item: AIExtractedInvoiceItem = await ai_extracted_invoice_item_postgres_repository.create_extracted_invoice_item(
            user_id=jwt_payload.id,
            extracted_invoice_id=create_manually_ai_extracted_invoice_item.extracted_invoice_id,
            ai_extracted_invoice_item=create_ai_extracted_invoice_item
        )

        ai_extracted_invoice_item_model: AIExtractedInvoiceItemModel = await AIExtractedInvoiceItemModel.ai_extracted_invoice_item_schema_to_model(
            extracted_invoice_item_schema=ai_extracted_invoice_item
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(ai_extracted_invoice_item_model))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.delete("/ai-extracted-invoice-item-module/delete-ai-extracted-invoice-item/")
async def delete_ai_extracted_invoice_item(
    ai_extracted_invoice_item_id: str, 
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        
        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await ai_extracted_invoice_item_postgres_repository.delete_extracted_invoice_item(
            extracted_invoice_item_id=ai_extracted_invoice_item_id,
            user_id=jwt_payload.id
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Extracted invoice item has been updated."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
