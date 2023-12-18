from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
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
from app.models.invoice_item_model import (
    CreateInvoiceItemModel,
    UpdateInvoiceItemModel,
    InvoiceItemModel
)
from app.schema.schema import InvoiceItem



router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/invoice-item-module/create-invoice-item/", response_model=InvoiceItemModel)
async def create_invoice_item(
    invoice_id: str,
    new_invoice_item: CreateInvoiceItemModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):

    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_item_postgres_repository = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice_item: InvoiceItem = await invoice_item_postgres_repository.create_invoice_item(
            user_id=jwt_payload.id,
            invoice_id=invoice_id,
            new_invoice_item=new_invoice_item
        )

        invoice_item_model: InvoiceItemModel = InvoiceItemModel.invoice_item_schema_to_model(invoice_item)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=invoice_item_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.patch("/invoice-item-module/update-invoice-item/")
async def update_invoice_item(
    update_invoice_item: UpdateInvoiceItemModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_item_postgres_repository = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await invoice_item_postgres_repository.update_invoice_item(
            user_id=jwt_payload.id,
            update_invoice_item=update_invoice_item
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice item updated succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/invoice-item-module/get-invoice-items-by-invoice-id/")
async def get_invoice_items_by_invoice_id(
    invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_item_postgres_repository = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice_items: list[InvoiceItem] = await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_items_model_list = []
        for invoice_item in invoice_items:
            invoice_item_model: InvoiceItemModel = InvoiceItemModel.invoice_item_schema_to_model(invoice_item)
            invoice_items_model_list.append(invoice_item_model)

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(invoice_items_model_list))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.delete("/invoice-item-module/delete-invoice-item/")
async def delete_invoice_item(
    invoice_item_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_item_postgres_repository = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await invoice_item_postgres_repository.remove_invoice_item(
            user_id=jwt_payload.id,
            invoice_item_id=invoice_item_id
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice item deleted succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))