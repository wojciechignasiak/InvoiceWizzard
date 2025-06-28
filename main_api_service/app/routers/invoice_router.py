#internal modules
from main_api_service.app.services.auth_service import IAuthService, new_auth_service
from main_api_service.app.services.invoice_service import IInvoiceService, new_invoice_service
from main_api_service.app.models.jwt_model import JWTPayloadModel
from main_api_service.app.models.invoice_model import CreateInvoiceModel, InvoiceModel, UpdateInvoiceModel
from main_api_service.app.custom_exceptions.custom_exceptions import CustomException

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.encoders import jsonable_encoder

#1st party libraries
import uuid
from typing import Optional
from pathlib import Path
from datetime import date
import ast


router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/invoice-module/create-invoice/", response_model={'invoice_id': uuid.uuid4()})
async def create_invoice(
    new_invoice: CreateInvoiceModel,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        invoice_id: uuid.UUID = await invoice_service.create_invoice(jwt_payload.user_id, new_invoice)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"invoice_id": invoice_id})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.get("/invoice-module/get-invoice/")
async def get_invoice(
    invoice_id: uuid.UUID,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        invoice: InvoiceModel = await invoice_service.get_invoice_by_id(jwt_payload.user_id, invoice_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=invoice.model_dump_json())
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.get("/invoice-module/get-all-invoices/")
async def get_all_invoices(
    page: int,
    items_per_page: int,
    user_business_entity_id: uuid.UUID | None = None,
    user_business_entity_name: str | None = None,
    external_business_entity_id: uuid.UUID | None = None,
    external_business_entity_name: str | None = None,
    invoice_number: str | None = None,
    start_issue_date: date | None = None,
    end_issue_date: date | None = None,
    start_sale_date: date | None = None,
    end_sale_date: date | None = None,
    payment_method: str | None = None,
    start_payment_deadline: date | None = None,
    end_payment_deadline: date | None = None,
    start_added_date: date | None = None,
    end_added_date: date | None = None,
    is_settled: bool | None = None,
    is_issued: bool | None = None,
    in_trash: bool | None = None,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):

    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        invoices: list[InvoiceModel] = await invoice_service.get_all_invoices(
            jwt_payload.user_id,
            page,
            items_per_page,
            user_business_entity_id,
            user_business_entity_name,
            external_business_entity_id,
            external_business_entity_name,
            invoice_number,
            start_issue_date,
            end_issue_date,
            start_sale_date,
            end_sale_date,
            payment_method,
            start_payment_deadline,
            end_payment_deadline,
            start_added_date,
            end_added_date,
            is_settled,
            is_issued,
            in_trash
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(invoices))
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.patch("/invoice-module/update-invoice/")
async def update_invoice(
    invoice_to_update: UpdateInvoiceModel,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.update_invoice(jwt_payload.user_id, invoice_to_update)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice updated successfully."})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    
@router.patch("/invoice-module/update-invoice-in-trash-status/")
async def update_invoice_in_trash_status(
    invoice_id: uuid.UUID,
    in_trash: bool,
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
    auth_service: IAuthService = Depends(new_auth_service),
    invoice_service: IInvoiceService = Depends(new_invoice_service)
    ):
    try:
        jwt_payload: JWTPayloadModel = await auth_service.get_jwt(token)
        await invoice_service.update_invoice_in_trash_status(jwt_payload.user_id, invoice_id, in_trash)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice and it's items in trash status updated"})
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=e.status_code, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.args[0])
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

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
            external_business_entity_name=external_business_entity_model.name,
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
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()

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
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()

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
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()

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
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)
        
        if invoice_model.invoice_pdf is None:
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
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = await InvoiceModel.invoice_schema_to_model(invoice)

        if invoice_model.invoice_pdf:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invoice arleady have file.")
        
        invoice_items: list[InvoiceItem] = await invoice_item_postgres_repository.get_invoice_items_by_invoice_id(
            user_id=jwt_payload.id,
            invoice_id=invoice_model.id,
            in_trash=False
        )

        invoice_items: list[InvoiceItemModel] = [await InvoiceItemModel.invoice_item_schema_to_model(invoice_item) for invoice_item in invoice_items]
        
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

        invoice_builder: InvoiceBuilderABC = InvoiceBuilder(
            user_business_entity=user_business_entity_model,
            external_business_entity=external_business_entity_model,
            invoice=invoice_model,
            invoice_items=invoice_items
        )
        
        invoice_html: str = await invoice_builder.create_invoice_html_document()
        
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