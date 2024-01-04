from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from app.registries.get_repositories_registry import get_repositories_registry
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from redis.asyncio import Redis
from app.database.redis.client.get_redis_client import get_redis_client
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisJWTNotFoundError
)
from app.models.jwt_model import (
    JWTPayloadModel
)
from uuid import uuid4


router = APIRouter()
http_bearer = HTTPBearer()


@router.post("/ai-extracted-data-module/extract-invoice-data-from-file/")
async def extract_invoice_data_from_file(
    invoice_file: UploadFile,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()

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
            
        

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.get("/ai-extracted-data-module/get-extracted-invoices/")
async def get_extracted_invoices(
    token = Depends(http_bearer),
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/ai-extracted-data-module/accept-extracted-invoice-data/")
async def accept_extracted_invoice_data(
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)


        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.patch("/ai-extracted-data-module/assign-external-business-entity-to-extracted-invoice-data/")
async def assign_external_business_entity_to_extracted_invoice_data(
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)


        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/ai-extracted-data-module/assign-user-business-entity-to-extracted-invoice-data/")
async def assign_user_business_entity_to_extracted_invoice_data(
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)


        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/ai-extracted-data-module/update-extracted-invoice-data/")
async def update_extracted_invoice_data(
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)


        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.delete("/ai-extracted-data-module/delete-extracted-invoice-data/")
async def delete_extracted_invoice_data(
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    ):
    try:
        user_redis_repository = await repositories_registry.return_user_redis_repository(redis_client)
        files_repository = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)


        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "File has been uploaded succesfull. You will be notified when data extraction is complete."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))