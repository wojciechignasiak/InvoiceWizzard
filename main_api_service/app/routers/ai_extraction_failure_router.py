from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse, FileResponse
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
from app.models.ai_extraction_failure_model import (
    AIExtractionFailureModel,
)
from app.types.postgres_repository_abstract_types import (
    AIExtractionFailurePostgresRepositoryABC
)
from app.files.files_repository_abc import FilesRepositoryABC
from app.types.redis_repository_abstract_types import (
    UserRedisRepositoryABC
)
from app.schema.schema import AIExtractionFailure
from pathlib import Path

router = APIRouter()
http_bearer = HTTPBearer()

@router.get("/ai-extraction-failure/get-all-ai-extraction-failure/")
async def get_all_external_business_entities(
    page: int,
    items_per_page: int,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extraction_failure_postgres_repository: AIExtractionFailurePostgresRepositoryABC = await repositories_registry.return_ai_extraction_failure_postgres_repository(postgres_session)

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extraction_failures: list[AIExtractionFailure] = await ai_extraction_failure_postgres_repository.get_all_ai_extraction_failure(
            user_id=jwt_payload.id,
            page=page,
            items_per_page=items_per_page
        )

        ai_extraction_failures_model: list[AIExtractionFailureModel] = [await AIExtractionFailureModel.ai_extraction_failure_schema_to_model(ai_extraction_failure) for ai_extraction_failure in ai_extraction_failures]
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(ai_extraction_failures_model))
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except PostgreSQLNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/ai-extraction-failure/remove-ai-extraction-failure/")
async def remove_ai_extraction_failure(
    id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):

    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extraction_failure_postgres_repository: AIExtractionFailurePostgresRepositoryABC = await repositories_registry.return_ai_extraction_failure_postgres_repository(postgres_session)
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()


        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extraction_failure: AIExtractionFailure = await ai_extraction_failure_postgres_repository.get_ai_extraction_failure(
            ai_extraction_failure_id=id,
            user_id=jwt_payload.id
        )

        ai_extraction_failure_model: AIExtractionFailureModel = await AIExtractionFailureModel.ai_extraction_failure_schema_to_model(ai_extraction_failure)

        await files_repository.remove_ai_extraction_failure_folder(
            file_path=ai_extraction_failure_model.invoice_pdf
        )

        await ai_extraction_failure_postgres_repository.delete_ai_extraction_failure(
            ai_extraction_failure_id=id,
            user_id=jwt_payload.id,
        )
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "AI Extraction Failure has been removed."})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (PostgreSQLNotFoundError, RedisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RedisJWTNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except (Exception, PostgreSQLDatabaseError, RedisDatabaseError, PostgreSQLIntegrityError, RedisSetError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ai-extraction-failure/download-ai-extraction-failure-pdf/")
async def download_ai_extraction_failure_pdf(
    id: str,
    token = Depends(http_bearer), 
    repositories_registry: RepositoriesRegistryABC = Depends(get_repositories_registry),
    redis_client: Redis = Depends(get_redis_client),
    postgres_session: AsyncSession = Depends(get_session),
    ):
    try:
        user_redis_repository: UserRedisRepositoryABC = await repositories_registry.return_user_redis_repository(redis_client)
        ai_extraction_failure_postgres_repository: AIExtractionFailurePostgresRepositoryABC = await repositories_registry.return_ai_extraction_failure_postgres_repository(postgres_session)
        files_repository: FilesRepositoryABC = await repositories_registry.return_files_repository()

        jwt_payload: bytes = await user_redis_repository.retrieve_jwt(
            jwt_token=token.credentials
            )
        
        jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

        ai_extraction_failure: AIExtractionFailure = await ai_extraction_failure_postgres_repository.get_ai_extraction_failure(
            ai_extraction_failure_id=id,
            user_id=jwt_payload.id
        )

        ai_extraction_failure_model: AIExtractionFailureModel = await AIExtractionFailureModel.ai_extraction_failure_schema_to_model(ai_extraction_failure)
        
        file: Path = await files_repository.get_invoice_pdf_file(
            file_path=ai_extraction_failure_model.invoice_pdf
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