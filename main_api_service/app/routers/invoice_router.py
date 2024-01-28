from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
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
from app.models.invoice_model import (
    InvoiceModel,
    CreateInvoiceModel,
    UpdateInvoiceModel
)
from app.models.invoice_item_model import (
    InvoiceItemModel,
    CreateInvoiceItemModel
)
from app.models.user_business_entity_model import (
    UserBusinessEntityModel
)
from app.models.external_business_entity_model import (
    ExternalBusinessEntity
)
from aiokafka import AIOKafkaProducer
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.registries.get_events_registry import get_events_registry
from app.registries.events_registry_abc import EventsRegistryABC
from app.models.user_business_entity_model import UserBusinessEntityModel
from app.models.external_business_entity_model import ExternalBusinessEntityModel
from app.schema.schema import (
    Invoice, 
    InvoiceItem, 
    UserBusinessEntity, 
    ExternalBusinessEntity
)
from app.types.postgres_repository_abstract_types import (
    InvoicePostgresRepositoryABC,
    InvoiceItemPostgresRepositoryABC,
    UserBusinessEntityPostgresRepositoryABC,
    ExternalBusinessEntityPostgresRepositoryABC
)
from app.types.redis_repository_abstract_types import (
    UserRedisRepositoryABC,
    InvoiceRedisRepositoryABC
)
from app.types.kafka_event_abstract_types import (
    InvoiceEventsABC
)
from uuid import uuid4
import ast
from app.utils.invoice_generator import invoice_generator
from typing import Optional, List
from pathlib import Path



router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/invoice-module/create-invoice/")
async def create_invoice(
    new_invoice: CreateInvoiceModel,
    invoice_items: List[CreateInvoiceItemModel],
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):

    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        invoice_item_postgres_repository: InvoiceItemPostgresRepositoryABC = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        is_invoice_unique = await invoice_postgres_repository.is_invoice_unique(
            user_id=jwt_payload.id,
            new_invoice=new_invoice
        )
        if is_invoice_unique == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice with provided business, number and type arleady exists.")
        
        invoice: Invoice = await invoice_postgres_repository.create_invoice(
            user_id=jwt_payload.id,
            new_invoice=new_invoice
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        invoice_items_model: list = []
        for invoice_item_model in invoice_items:
            invoice_item: InvoiceItem = await invoice_item_postgres_repository.create_invoice_item(
                user_id=jwt_payload.id,
                invoice_id=invoice_model.id,
                new_invoice_item=invoice_item_model
            )
            
            invoice_item_model: InvoiceItemModel = await InvoiceItemModel.invoice_item_schema_to_model(invoice_item)
            
            invoice_items_model.append(invoice_item_model)
        
        invoice: dict = invoice_model.model_dump()

        invoice["invoice_items"] = invoice_items_model

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(invoice))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/invoice-module/get-invoice/")
async def get_invoice(
    invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):

    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        invoice_item_postgres_repository: InvoiceItemPostgresRepositoryABC = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)
        
        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        invoice_items: list = await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
            user_id=jwt_payload.id,
            invoice_id=invoice_model.id,
            in_trash=invoice_model.in_trash
        )
        sum_gross_value = 0.0
        sum_net_value = 0.0
        for invoice_item in invoice_items:
            invoice_item_model: InvoiceItemModel = await InvoiceItemModel.invoice_item_schema_to_model(invoice_item)
            sum_gross_value += invoice_item_model.gross_value
            sum_net_value += invoice_item_model.net_value

        invoice_details = invoice_model.model_dump()

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
                    user_id=jwt_payload.id,
                    user_business_entity_id=invoice_model.user_business_entity_id
                )

        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)
        
        invoice_details["user_business_entity_name"] = user_business_entity_model.company_name

        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.get_external_business_entity(
            user_id=jwt_payload.id,
            external_business_entity_id=invoice_model.external_business_entity_id
        )

        external_business_entity_model: ExternalBusinessEntityModel = await ExternalBusinessEntityModel.external_business_entity_schema_to_model(external_business_entity)
        invoice_details["external_business_entity_name"] = external_business_entity_model.name

        invoice_details["net_value"] = sum_net_value
        invoice_details["gross_value"] = sum_gross_value

        return JSONResponse(status_code=status.HTTP_200_OK, content=invoice_details)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/invoice-module/get-all-invoices/")
async def get_all_invoices(
    page: int,
    items_per_page: int,
    user_business_entity_id: Optional[str] = None,
    user_business_entity_name: Optional[str] = None,
    external_business_entity_id: Optional[str] = None,
    external_business_entity_name: Optional[str] = None,
    invoice_number: Optional[str] = None,
    start_issue_date: Optional[str] = None,
    end_issue_date: Optional[str] = None,
    start_sale_date: Optional[str] = None,
    end_sale_date: Optional[str] = None,
    payment_method: Optional[str] = None,
    start_payment_deadline: Optional[str] = None,
    end_payment_deadline: Optional[str] = None,
    start_added_date: Optional[str] = None,
    end_added_date: Optional[str] = None,
    is_settled: Optional[bool] = None,
    is_issued: Optional[bool] = None,
    in_trash: Optional[bool] = None,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_item_postgres_repository: InvoiceItemPostgresRepositoryABC = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoices: list[Invoice] = await user_invoice_postgres_repository.get_all_invoices(
            user_id=jwt_payload.id,
            page=page,
            items_per_page=items_per_page,
            user_business_entity_id=user_business_entity_id,
            user_business_entity_name=user_business_entity_name,
            external_business_entity_id=external_business_entity_id,
            external_business_entity_name=external_business_entity_name,
            invoice_number=invoice_number,
            start_issue_date=start_issue_date,
            end_issue_date=end_issue_date,
            start_sale_date=start_sale_date,
            end_sale_date=end_sale_date,
            payment_method=payment_method,
            start_payment_deadline=start_payment_deadline,
            end_payment_deadline=end_payment_deadline,
            start_added_date=start_added_date,
            end_added_date=end_added_date,
            is_settled=is_settled,
            is_issued=is_issued,
            in_trash=in_trash
        )
        
        all_invoices = []
        for invoice in invoices:
            
            invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

            invoice_items: list = await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
            user_id=jwt_payload.id,
            invoice_id=invoice_model.id,
            in_trash=invoice_model.in_trash
            )

            sum_gross_value = 0.0
            sum_net_value = 0.0
            invoice_details = invoice_model.model_dump()

            for invoice_item in invoice_items:
                invoice_item_model: InvoiceItemModel = await InvoiceItemModel.invoice_item_schema_to_model(invoice_item)
                sum_gross_value += invoice_item_model.gross_value
                sum_net_value += invoice_item_model.net_value
                
                invoice_details["net_value"] = sum_net_value
                invoice_details["gross_value"] = sum_gross_value

                user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
                    user_id=jwt_payload.id,
                    user_business_entity_id=invoice_model.user_business_entity_id
                )
                external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.get_external_business_entity(
                    user_id=jwt_payload.id,
                    external_business_entity_id=invoice_model.external_business_entity_id
                )
                user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)
                
                external_business_entity_model: ExternalBusinessEntityModel = await ExternalBusinessEntityModel.external_business_entity_schema_to_model(external_business_entity)

                invoice_details["user_business_entity_name"] = user_business_entity_model.company_name
                invoice_details["external_business_entity_name"] = external_business_entity_model.name

            all_invoices.append(invoice_details)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(all_invoices))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/invoice-module/update-invoice/")
async def update_invoice(
    update_invoice: UpdateInvoiceModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        is_invoice_unique_beside_one_to_update = await invoice_postgres_repository.is_invoice_unique_beside_one_to_update(
            user_id=jwt_payload.id,
            update_invoice=update_invoice
        )
        
        if is_invoice_unique_beside_one_to_update == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice with provided business, number and type arleady exists beside one to update.")
        
        await invoice_postgres_repository.update_invoice(
            user_id=jwt_payload.id,
            update_invoice=update_invoice
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice updated succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.patch("/invoice-module/update-invoice-in-trash-status/")
async def update_invoice_in_trash_status(
    invoice_id: str,
    in_trash: bool,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        invoice_item_repository: InvoiceItemPostgresRepositoryABC = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await invoice_postgres_repository.update_invoice_in_trash_status(
            user_id=jwt_payload.id,
            invoice_id=invoice_id,
            in_trash=in_trash
        )
        
        await invoice_item_repository.update_all_invoice_items_in_trash_status_by_invoice_id(
            user_id=jwt_payload.id,
            invoice_id=invoice_id,
            in_trash=in_trash
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice and it's items in trash status updated."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/invoice-module/initialize-invoice-removal/")
async def initialize_invoice_removal(
    invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        invoice_redis_repository: InvoiceRedisRepositoryABC = await repositories_registry.return_invoice_redis_repository(redis_client)
        invoice_events: InvoiceEventsABC = await events_registry.return_invoice_events(kafka_producer_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )
        
        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        key_id = uuid4()

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=invoice_model.user_business_entity_id
        )

        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)

        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.get_external_business_entity(
            user_id=jwt_payload.id,
            external_business_entity_id=invoice_model.external_business_entity_id
        )

        external_business_entity_model: ExternalBusinessEntityModel = await ExternalBusinessEntityModel.external_business_entity_schema_to_model(external_business_entity)

        await invoice_redis_repository.initialize_invoice_removal(
            key_id=str(key_id),
            invoice_id=invoice_model.id
        )

        await invoice_events.remove_invoice(
            id=str(key_id),
            email_address=jwt_payload.email,
            invoice_number=invoice_model.invoice_number,
            user_company_name=user_business_entity_model.company_name,
            external_buisness_entity_name=external_business_entity_model.name,
            is_issued=invoice_model.is_issued
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice removal initialized."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/invoice-module/confirm-invoice-removal/")
async def confirm_invoice_removal(
    key_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        invoice_redis_repository: InvoiceRedisRepositoryABC = await repositories_registry.return_invoice_redis_repository(redis_client)
        invoice_events: InvoiceEventsABC = await events_registry.return_invoice_events(kafka_producer_client)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice_id: bytes = await invoice_redis_repository.retrieve_invoice_removal(
            key_id=key_id
        )

        invoice_id = invoice_id.decode()
        invoice_id = ast.literal_eval(invoice_id)
        invoice_id = invoice_id["id"]

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
            )
        
        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.get_external_business_entity(
            user_id=jwt_payload.id,
            external_business_entity_id=invoice_model.external_business_entity_id
        )

        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=invoice_model.user_business_entity_id
        )

        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)

        await invoice_postgres_repository.remove_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )
        if invoice_model.invoice_pdf != None:
            await files_repository.remove_invoice_folder(
                user_id=jwt_payload.id, 
                invoice_id=invoice_model.id,
                folder="invoice")

        await invoice_redis_repository.delete_invoice_removal(
            key_id=key_id
            )
        
        await invoice_events.invoice_removed(
            id=key_id,
            email_address=jwt_payload.email,
            invoice_number=invoice_model.invoice_number,
            user_company_name=user_business_entity_model.company_name,
            external_business_entity_name=external_business_entity.name,
            is_issued=invoice_model.is_issued
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice removed succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (PostgreSQLNotFoundError, RedisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError, KafkaBaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/invoice-module/add-file-to-invoice/")
async def add_file_to_invoice(
    invoice_id: str,
    invoice_file: UploadFile,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        if invoice_model.invoice_pdf != None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The invoice arleady have pdf file. Delete current file first.")
        
        file_path = f"/usr/app/invoice-files/invoice/{jwt_payload.id}/{invoice_model.id}/invoice.pdf"

        file_extension = invoice_file.filename.split(".")[-1]

        file_data: bytes = await invoice_file.read()

        match file_extension:
            case "pdf":
                await files_repository.save_invoice_file(
                    file_path=file_path,
                    file_data=file_data
                )
            case "jpg" | "jpeg" | "png":
                await files_repository.convert_from_img_to_pdf_and_save_invoice_file(
                    file_path=file_path,
                    file_extension=file_extension,
                    file_data=file_data
                )
            case _:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Invoice file in unsupported format. Use PDF or JPG/JPEG/PNG.")

        await invoice_postgres_repository.update_invoice_file(
            user_id=jwt_payload.id,
            invoice_id=invoice_id,
            invoice_pdf_location=file_path
        )

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "File has been added to the invoice."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/invoice-module/delete-invoice-pdf/")
async def delete_invoice_pdf(
    invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        if invoice_model.invoice_pdf == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice doesn't have file.")
        
        await invoice_postgres_repository.remove_invoice_file(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )
        
        await files_repository.remove_invoice_folder(
            user_id=jwt_payload.id,
            invoice_id=invoice_model.id,
            folder='invoice'
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "File has been deleted."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/invoice-module/download-invoice-pdf/")
async def download_invoice_pdf(
    invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)
        
        if invoice_model.invoice_pdf == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice doesn't have file.")
        
        file: Path = await files_repository.get_invoice_pdf_file(
            file_path=invoice_model.invoice_pdf
            )
        
        if file.is_file() == False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        return FileResponse(path=file, status_code=status.HTTP_200_OK, filename=file.name)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/invoice-module/generate-invoice-pdf/")
async def generate_invoice_pdf(
    invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository: InvoicePostgresRepositoryABC = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        invoice_item_postgres_repository: InvoiceItemPostgresRepositoryABC = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC = await repositories_registry.return_external_business_entity_postgres_repository(postgres_session)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        if invoice_model.invoice_pdf != None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice arleady have file.")
        
        invoice_items: list[InvoiceItem] = await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
            user_id=jwt_payload.id,
            invoice_id=invoice_model.id,
            in_trash=False
        )

        invoice_items_model: list = []

        for invoice_item in invoice_items:
            invoice_item_model: InvoiceItemModel = await InvoiceItemModel.invoice_item_schema_to_model(invoice_item)
            invoice_items_model.append(invoice_item_model)
        
        user_business_entity: UserBusinessEntity = await user_business_entity_postgres_repository.get_user_business_entity(
            user_id=jwt_payload.id,
            user_business_entity_id=invoice_model.user_business_entity_id
        )

        user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(user_business_entity)

        external_business_entity: ExternalBusinessEntity = await external_business_entity_postgres_repository.get_external_business_entity(
            user_id=jwt_payload.id,
            external_business_entity_id=invoice_model.external_business_entity_id
        )
        
        external_business_entity_model: ExternalBusinessEntityModel = await ExternalBusinessEntityModel.external_business_entity_schema_to_model(external_business_entity)

        invoice_html = await invoice_generator(
            user_business_entity=user_business_entity_model,
            external_business_entity=external_business_entity_model,
            invoice=invoice_model,
            invoice_items=invoice_items_model
        )
        
        file_path = f"/usr/app/invoice-files/invoice/{jwt_payload.id}/{invoice_model.id}/invoice.pdf"

        await files_repository.invoice_html_to_pdf(
            invoice_html=invoice_html,
            file_path=file_path
        )
        
        await invoice_postgres_repository.update_invoice_file(
            user_id=jwt_payload.id,
            invoice_id=invoice_id,
            invoice_pdf_location=file_path
        )
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "File has been generated."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))