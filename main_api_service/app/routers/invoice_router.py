from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
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
from app.models.invoice_model import (
    InvoiceModel,
    CreateInvoiceModel,
    UpdateInvoiceModel
)
from app.schema.schema import Invoice
import img2pdf
import os
from PIL import Image
import imageio
import io
from uuid import uuid4
import ast
import shutil
from pathlib import Path

router = APIRouter()
http_bearer = HTTPBearer()

@router.post("/invoice-module/create-invoice/", response_model=InvoiceModel)
async def create_invoice(
    new_invoice: CreateInvoiceModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session)
    ):

    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)

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

        invoice_model: InvoiceModel = InvoiceModel.invoice_schema_to_model(invoice)

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=invoice_model.model_dump())
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/invoice-module/update-invoice/")
async def update_invoice(
    update_invoice: UpdateInvoiceModel,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

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

@router.put("/invoice-module/initialize-invoice-removal/")
async def initialize_invoice_removal(
    invoice_id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        invoice_redis_repository = await repositories_registry.return_invoice_redis_repository(redis_client)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )
        
        key_id = uuid4()
        await invoice_redis_repository.initialize_invoice_removal(
            key_id=str(key_id),
            invoice_id=invoice_id
        )

        #add event

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice removal initialized."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/invoice-module/confirm-invoice-removal/")
async def confirm_invoice_removal(
    key_id: str,
    background_tasks: BackgroundTasks,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)
        invoice_redis_repository = await repositories_registry.return_invoice_redis_repository(redis_client)

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
        
        invoice_model: InvoiceModel = InvoiceModel.invoice_schema_to_model(invoice)

        await invoice_postgres_repository.remove_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )
        if invoice_model.invoice_pdf != None:
            background_tasks.add_task(
                shutil.rmtree,
                f"/usr/app/invoice/{jwt_payload.id}/{invoice_model.id}"
            )

        background_tasks.add_task(
            invoice_redis_repository.delete_invoice_removal,
            key_id=key_id
        )
        #add event

        return JSONResponse(status_code=status.HTTP_200_OK, content={"details": "Invoice removed succesfully."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (PostgreSQLNotFoundError, RedisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/invoice-module/add-file-to-invoice/")
async def add_file_to_invoice(
    invoice_id: str,
    invoice_file: UploadFile,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = InvoiceModel.invoice_schema_to_model(invoice)

        if invoice_model.invoice_pdf != None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The invoice arleady have pdf file. Delete current file first.")
        
        file_path = f"/usr/app/invoice/{jwt_payload.id}/{invoice_model.id}/invoice.pdf"

        file_extension = invoice_file.filename.split(".")[-1]

        file_data: bytes = await invoice_file.read()

        match file_extension:
            case "pdf":
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "wb") as f:
                    f.write(file_data)
            case "jpg" | "jpeg" | "png":
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with imageio.get_reader(io.BytesIO(file_data)) as reader:
                    is_it_mpo: bool = len(reader) > 1

                    if is_it_mpo:
                        base_image = Image.fromarray(reader.get_data(0))

                        with io.BytesIO() as jpeg_stream:
                            base_image.save(jpeg_stream, format=file_extension)
                            file_data = jpeg_stream.getvalue()

                with open(file_path, "wb") as f:
                    f.write(img2pdf.convert(file_data))
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
    background_tasks: BackgroundTasks,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = InvoiceModel.invoice_schema_to_model(invoice)

        if invoice_model.invoice_pdf == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice doesn't have file.")
        
        await invoice_postgres_repository.remove_invoice_file(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        background_tasks.add_task(
            shutil.rmtree,
            invoice_model.invoice_pdf
        )

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "File has been deleted."})
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
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        invoice_postgres_repository = await repositories_registry.return_invoice_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        invoice: Invoice = await invoice_postgres_repository.get_invoice(
            user_id=jwt_payload.id,
            invoice_id=invoice_id
        )

        invoice_model: InvoiceModel = InvoiceModel.invoice_schema_to_model(invoice)

        if invoice_model.invoice_pdf == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice doesn't have file.")
        
        file_path = Path(invoice_model.invoice_pdf)
    
        if not file_path.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

        return FileResponse(file_path, filename=file_path.name)
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
    repositories_registry: RepositoriesRegistry = Depends(get_repositories_registry),
    redis_client: redis.Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    pass