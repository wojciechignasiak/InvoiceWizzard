from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
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
from aiokafka import AIOKafkaProducer
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client
from app.kafka.exceptions.custom_kafka_exceptions import KafkaBaseError
from app.registries.get_events_registry import get_events_registry
from app.registries.events_registry_abc import EventsRegistryABC
from app.models.ai_extracted_invoice_model import AIExtractedInvoiceModel, UpdateAIExtractedInvoiceModel
from app.models.ai_extracted_invoice_item_model import AIExtractedInvoiceItemModel
from app.models.ai_extracted_user_business_entity_model import AIExtractedUserBusinessEntityModel
from app.models.ai_extracted_external_business_entity_model import AIExtractedExternalBusinessModel
from app.models.ai_is_external_business_entity_recognized_model import AIIsExternalBusinessEntityRecognizedModel
from app.models.ai_is_user_business_entity_recognized_model import AIIsUserBusinessEntityRecognizedModel
from app.models.invoice_model import CreateInvoiceModel, InvoiceModel
from app.models.invoice_item_model import CreateInvoiceItemModel
from app.models.user_business_entity_model import UserBusinessEntityModel
from app.schema.schema import (
    AIExtractedInvoice,
    AIExtractedInvoiceItem,
    AIExtractedExternalBusinessEntity,
    AIExtractedUserBusinessEntity,
    AIIsExternalBusinessEntityRecognized,
    AIIsUserBusinessEntityRecognized,
    Invoice,
    UserBusinessEntity
)
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisJWTNotFoundError
)
from app.types.postgres_repository_abstract_types import (
    AIExtractedUserBusinessEntityPostgresRepositoryABC,
    AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC,
    AIExtractedUserBusinessEntityPostgresRepositoryABC,
    AIIsUserBusinessRecognizedPostgresRepositoryABC,
    UserBusinessEntityPostgresRepositoryABC,
    AIExtractedInvoicePostgresRepositoryABC,
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
from uuid import uuid4
from typing import List


router = APIRouter()
http_bearer = HTTPBearer()


@router.post("/ai-extracted-invoice-module/extract-invoice-data-from-file/")
async def extract_invoice_data_from_file(
    invoice_file: UploadFile,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    kafka_producer_client: AIOKafkaProducer = Depends(get_kafka_producer_client),
    events_registry: EventsRegistryABC = Depends(get_events_registry),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()
        user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_user_business_entity_postgres_repository(postgres_session)
        ai_invoice_events: AIInvoiceEventsABC = await events_registry.return_ai_invoice_events(kafka_producer_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        key_id = uuid4()

        file_path = f"/usr/app/invoice-files/ai-invoice/{jwt_payload.id}/{str(key_id)}/invoice.pdf"

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
            
        user_business_entities: List[UserBusinessEntity] = await user_business_entity_postgres_repository.get_all_user_business_entities(
            user_id=jwt_payload.id,
            items_per_page=1000
        )

        user_business_entities_nip: List[str] = []

        for user_business_entity in user_business_entities:
            user_business_entity_model: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(
                user_business_entity_schema=user_business_entity
            )
            user_business_entities_nip.append(user_business_entity_model.nip)

        await ai_invoice_events.extract_invoice_data(
            file_location=file_path,
            user_business_entities_nip=user_business_entities_nip
        )

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.get("/ai-extracted-invoice-module/get-ai-extracted-invoice/")
async def get_ai_extracted_invoice(
    extracted_invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_postgres_repository: AIExtractedInvoicePostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_postgres_repository(postgres_session)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        ai_extracted_user_business_entity_postgres_repository: AIExtractedUserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_ai_extracted_user_business_entity_postgres_repository(postgres_session)
        ai_is_user_business_recognized_postgres_repository: AIIsUserBusinessRecognizedPostgresRepositoryABC = await repositories_registry.return_ai_is_user_business_recognized_postgres_repository(postgres_session)
        ai_extracted_external_business_entity_postgres_repository: AIExtractedUserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_ai_extracted_external_business_entity_postgres_repository(postgres_session)
        ai_is_external_business_recognized_postgres_repository: AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC = await repositories_registry.return_ai_is_external_business_recognized_postgres_repository(postgres_session)


        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extracted_invoice: AIExtractedInvoice = await ai_extracted_invoice_postgres_repository.get_extracted_invoice(
            extracted_invoice_id=extracted_invoice_id,
            user_id=jwt_payload.id
        )

        
        ai_extracted_invoice_model: AIExtractedInvoiceModel = await AIExtractedInvoiceModel.ai_extracted_invoice_schema_to_model(ai_extracted_invoice)

        ai_extracted_invoice_items: list[AIExtractedInvoiceItem] = await ai_extracted_invoice_item_postgres_repository.get_all_extracted_invoice_item_data_by_extracted_invoice_id(
            extracted_invoice_id=ai_extracted_invoice_model.id,
            user_id=jwt_payload.id
        )

        net_value: float = 0.0
        gross_value: float = 0.0
        ai_extracted_invoice_item_models: list[AIExtractedInvoiceItemModel] = [] 
        for ai_extracted_invoice_item in ai_extracted_invoice_items:
            ai_extracted_invoice_item_model = await AIExtractedInvoiceItemModel.ai_extracted_invoice_item_schema_to_model(ai_extracted_invoice_item)

            if ai_extracted_invoice_item_model.net_value != None:
                net_value+=ai_extracted_invoice_item_model.net_value

            if ai_extracted_invoice_item_model.gross_value != None:
                gross_value+=ai_extracted_invoice_item_model.gross_value

            ai_extracted_invoice_item_models.append(ai_extracted_invoice_item_model)

        ai_extracted_user_business_entity: AIExtractedUserBusinessEntity = await ai_extracted_user_business_entity_postgres_repository.get_extracted_user_business_entity(
            extracted_invoice_id=ai_extracted_invoice.id,
            user_id=jwt_payload.id
        )
        ai_extracted_user_business_entity_model: AIExtractedUserBusinessEntityModel = await AIExtractedUserBusinessEntityModel.ai_extracted_user_business_schema_to_model(
            ai_extracted_user_business_entity
        )

        ai_is_user_business_entity_recognized: AIIsUserBusinessEntityRecognized = await ai_is_user_business_recognized_postgres_repository.get_is_user_business_recognized(
            extracted_invoice_id=ai_extracted_invoice.id,
            user_id=jwt_payload.id
        )
        ai_is_user_business_entity_recognized_model: AIIsUserBusinessEntityRecognizedModel = await AIIsUserBusinessEntityRecognizedModel.ai_is_user_business_entity_recognized_schema_to_model(
            ai_is_user_business_entity_recognized
        )

        ai_extracted_external_business_entity: AIExtractedExternalBusinessEntity = await ai_extracted_external_business_entity_postgres_repository.get_extracted_external_business_entity(
            extracted_invoice_id=ai_extracted_invoice.id,
            user_id=jwt_payload.id
        )
        ai_extracted_external_business_entity_model: AIExtractedExternalBusinessModel = await AIExtractedExternalBusinessModel.ai_extracted_external_business_schema_to_model(
            ai_extracted_external_business_entity
        )

        ai_is_external_business_entity_recognized: AIIsExternalBusinessEntityRecognized = await ai_is_external_business_recognized_postgres_repository.get_is_external_business_entity_recognized(
            extracted_invoice_id=ai_extracted_invoice.id,
            user_id=jwt_payload.id
        )
        ai_is_external_business_entity_recognized_model: AIIsExternalBusinessEntityRecognizedModel = await AIIsExternalBusinessEntityRecognizedModel.ai_is_external_business_entity_recognized_schema_to_model(
            ai_is_external_business_entity_recognized
        )

        ai_extracted_invoice: dict = ai_extracted_invoice_model.model_dump()

        ai_extracted_invoice["net_value"] = net_value
        ai_extracted_invoice["gross_value"] = gross_value
        ai_extracted_invoice["invoice_items"] = ai_extracted_invoice_item_models
        ai_extracted_invoice["ai_extracted_user_business_entity"] = ai_extracted_user_business_entity_model
        ai_extracted_invoice["ai_is_user_business_entity_recognized"] = ai_is_user_business_entity_recognized_model
        ai_extracted_invoice["ai_extracted_user_business_entity"] = ai_extracted_external_business_entity_model
        ai_extracted_invoice["ai_is_external_business_entity_recognized"] = ai_is_external_business_entity_recognized_model

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(ai_extracted_invoice))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/ai-extracted-invoice-module/get-all-ai-extracted-invoices/")
async def get_all_ai_extracted_invoices(
    page: int,
    items_per_page: int,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_postgres_repository: AIExtractedInvoicePostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_postgres_repository(postgres_session)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extracted_invoices: list[AIExtractedInvoice] = await ai_extracted_invoice_postgres_repository.get_all_extracted_invoices(
            user_id=jwt_payload.id,
            page=page,
            items_per_page=items_per_page
        )

        ai_extracted_invoices_with_net_and_gross_value: list[dict] = []

        for ai_extracted_invoice in ai_extracted_invoices:
            ai_extracted_invoice_model: AIExtractedInvoiceModel = await AIExtractedInvoiceModel.ai_extracted_invoice_schema_to_model(ai_extracted_invoice)

            ai_extracted_invoice_items: list[AIExtractedInvoiceItem] = await ai_extracted_invoice_item_postgres_repository.get_all_extracted_invoice_item_data_by_extracted_invoice_id(
                extracted_invoice_id=ai_extracted_invoice_model.id,
                user_id=jwt_payload.id
            )

            net_value: float = 0.0
            gross_value: float = 0.0

            for ai_extracted_invoice_item in ai_extracted_invoice_items:
                ai_extracted_invoice_item_model = await AIExtractedInvoiceItemModel.ai_extracted_invoice_item_schema_to_model(ai_extracted_invoice_item)

                if ai_extracted_invoice_item_model.net_value != None:
                    net_value+=ai_extracted_invoice_item_model.net_value

                if ai_extracted_invoice_item_model.gross_value != None:
                    gross_value+=ai_extracted_invoice_item_model.gross_value

            ai_extracted_invoice: dict = ai_extracted_invoice_model.model_dump()
            ai_extracted_invoice["net_value"] = net_value
            ai_extracted_invoice["gross_value"] = gross_value

            ai_extracted_invoices_with_net_and_gross_value.append(ai_extracted_invoice)

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(ai_extracted_invoices_with_net_and_gross_value))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post("/ai-extracted-invoice-module/accept-ai-extracted-invoice/")
async def accept_ai_extracted_invoice(
    ai_extracted_invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_postgres_repository: AIExtractedInvoicePostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_postgres_repository(postgres_session)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        ai_is_external_business_recognized_postgres_repository: AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC = await repositories_registry.return_ai_is_external_business_recognized_postgres_repository(postgres_session)
        ai_is_user_business_recognized_postgres_repository: AIIsUserBusinessRecognizedPostgresRepositoryABC = await repositories_registry.return_ai_is_user_business_recognized_postgres_repository(postgres_session)
        
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        invoice_item_postgres_repository = await repositories_registry.return_invoice_item_postgres_repository(postgres_session)

        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extracted_invoice: AIExtractedInvoice = await ai_extracted_invoice_postgres_repository.get_extracted_invoice(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        ai_extracted_invoice_items: List[AIExtractedInvoiceItem] = await ai_extracted_invoice_item_postgres_repository.get_all_extracted_invoice_item_data_by_extracted_invoice_id(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        ai_is_external_business_entity_recognized: AIIsExternalBusinessEntityRecognized = await ai_is_external_business_recognized_postgres_repository.get_is_external_business_entity_recognized(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        ai_is_user_business_entity_recognized: AIIsUserBusinessEntityRecognized = await ai_is_user_business_recognized_postgres_repository.get_is_user_business_recognized(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        ai_extracted_invoice_model: AIExtractedInvoiceModel = await AIExtractedInvoiceModel.ai_extracted_invoice_schema_to_model(
            extracted_invoice_schema = ai_extracted_invoice
            )

        extracted_invoice_item_models: List[AIExtractedInvoiceItemModel] = []

        for extracted_invoice_item in ai_extracted_invoice_items:
            extracted_invoice_item_model: AIExtractedInvoiceItemModel = await AIExtractedInvoiceItemModel.ai_extracted_invoice_item_schema_to_model(
                extracted_invoice_item_schema=extracted_invoice_item
            )

            extracted_invoice_item_models.append(extracted_invoice_item_model)


        ai_is_user_business_entity_recognized_model: AIIsUserBusinessEntityRecognizedModel = await AIIsUserBusinessEntityRecognizedModel.ai_is_user_business_entity_recognized_schema_to_model(
            is_user_business_recognized_schema = ai_is_user_business_entity_recognized
        )

        ai_is_external_business_entity_recognized_model = await AIIsExternalBusinessEntityRecognizedModel.ai_is_external_business_entity_recognized_schema_to_model(
            is_external_business_entity_recognized_schema=ai_is_external_business_entity_recognized
        )

        if ai_is_user_business_entity_recognized_model.is_recognized == False or ai_is_user_business_entity_recognized_model.user_business_entity_id == None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User business entity is still not recognized. Accept user business entity first.")
        
        if ai_is_external_business_entity_recognized_model.is_recognized == False or ai_is_external_business_entity_recognized_model.external_business_entity_id == None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="External business entity is still not recognized. Accept external business entity first.")
        

        create_invoice_model: CreateInvoiceModel = CreateInvoiceModel(
            user_business_entity_id=ai_is_user_business_entity_recognized_model.user_business_entity_id,
            external_business_entity_id=ai_is_external_business_entity_recognized_model.external_business_entity_id,
            invoice_number=ai_extracted_invoice_model.invoice_number,
            issue_date=ai_extracted_invoice_model.issue_date,
            sale_date=ai_extracted_invoice_model.sale_date,
            payment_method=ai_extracted_invoice_model.payment_method,
            payment_deadline=ai_extracted_invoice_model.payment_deadline,
            notes=ai_extracted_invoice_model.notes,
            is_settled=False,
            is_issued=ai_extracted_invoice_model.is_issued
        )

        is_invoice_unique: bool = await invoice_postgres_repository.is_invoice_unique(
            user_id=jwt_payload.id,
            new_invoice=create_invoice_model
        )

        if is_invoice_unique == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice with provided business, number and type arleady exists.")
        

        invoice: Invoice = await invoice_postgres_repository.create_invoice(
            user_id=jwt_payload.id,
            new_invoice=create_invoice_model
        )
        
        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        for extracted_invoice_item_model in extracted_invoice_item_models:
            create_invoice_item_model: CreateInvoiceItemModel = CreateInvoiceItemModel(
                item_description=extracted_invoice_item_model.item_description,
                number_of_items=extracted_invoice_item_model.number_of_items,
                net_value=extracted_invoice_item_model.net_value,
                gross_value=extracted_invoice_item_model.gross_value
            )
            
            await invoice_item_postgres_repository.create_invoice_item(
                user_id=jwt_payload.id,
                invoice_id=invoice_model.id,
                new_invoice_item=create_invoice_item_model
            )

        await files_repository.copy_ai_invoice_to_invoice_folder(
            ai_invoice_id=ai_extracted_invoice_model.id,
            user_id=jwt_payload.id,
            invoice_id=invoice_model.id
        )

        await files_repository.remove_invoice_folder(
            user_id=jwt_payload.id,
            invoice_id=ai_extracted_invoice_model.id,
            folder="ai-invoice"
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Invoice accepted succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.delete("/ai-extracted-invoice-module/delete-ai-extracted-invoice/")
async def delete_ai_extracted_invoice(
    ai_extracted_invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_postgres_repository: AIExtractedInvoicePostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_postgres_repository(postgres_session)
        ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_item_postgres_repository(postgres_session)
        ai_is_external_business_recognized_postgres_repository: AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC = await repositories_registry.return_ai_is_external_business_recognized_postgres_repository(postgres_session)
        ai_is_user_business_recognized_postgres_repository: AIIsUserBusinessRecognizedPostgresRepositoryABC = await repositories_registry.return_ai_is_user_business_recognized_postgres_repository(postgres_session)
        ai_extracted_user_business_entity_postgres_repository: AIExtractedUserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_ai_extracted_user_business_entity_postgres_repository(postgres_session)
        ai_extracted_external_business_entity_postgres_repository: AIExtractedUserBusinessEntityPostgresRepositoryABC = await repositories_registry.return_ai_extracted_external_business_entity_postgres_repository(postgres_session)

        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)


        await ai_extracted_external_business_entity_postgres_repository.delete_extracted_external_business_entity(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        await ai_extracted_user_business_entity_postgres_repository.delete_extracted_user_business_entity(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        await ai_is_external_business_recognized_postgres_repository.delete_is_external_business_entity_recognized(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        await ai_is_user_business_recognized_postgres_repository.delete_is_user_business_recognized(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        await ai_extracted_invoice_item_postgres_repository.delete_extracted_invoice_items(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        await ai_extracted_invoice_postgres_repository.delete_extracted_invoice(
            extracted_invoice_id=ai_extracted_invoice_id,
            user_id=jwt_payload.id
        )

        await files_repository.remove_invoice_folder(
            user_id=jwt_payload.id,
            invoice_id=ai_extracted_invoice_id,
            folder="ai-invoice"
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Invoice deleted succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.patch("/ai-extracted-invoice-module/update-ai-extracted-invoice/")
async def update_ai_extracted_invoice(
    update_ai_extracted_invoice: UpdateAIExtractedInvoiceModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extracted_invoice_postgres_repository: AIExtractedInvoicePostgresRepositoryABC = await repositories_registry.return_ai_extracted_invoice_postgres_repository(postgres_session)
        
        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await ai_extracted_invoice_postgres_repository.update_extracted_invoice(
            user_id=jwt_payload.id,
            ai_update_extracted_invoice=update_ai_extracted_invoice
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Invoice updated succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, RedisDatabaseError, PostgreSQLDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))