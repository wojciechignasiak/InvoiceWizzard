from app.types.postgres_repository_abstract_types import (
    UserPostgresRepositoryABC,
    UserBusinessEntityPostgresRepositoryABC,
    ExternalBusinessEntityPostgresRepositoryABC,
    InvoicePostgresRepositoryABC,
    InvoiceItemPostgresRepositoryABC,
    AIExtractedExternalBusinessEntityPostgresRepositoryABC,
    AIExtractedInvoiceItemPostgresRepositoryABC,
    AIExtractedInvoicePostgresRepositoryABC,
    AIExtractedUserBusinessEntityPostgresRepositoryABC,
    AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC,
    AIIsUserBusinessRecognizedPostgresRepositoryABC,
    AIExtractionFailurePostgresRepositoryABC,
    ReportPostgresRepositoryABC
)
from app.types.redis_repository_abstract_types import (
    UserRedisRepositoryABC,
    UserBusinessEntityRedisRepositoryABC,
    ExternalBusinessEntityRedisRepositoryABC,
    InvoiceRedisRepositoryABC,
)
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from abc import ABC, abstractmethod
from app.files.files_repository_abc import FilesRepositoryABC


class RepositoriesFactoryABC(ABC):

    @abstractmethod
    async def return_user_postgres_repository(self, session: AsyncSession) -> UserPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def return_user_redis_repository(self, redis_client: Redis) -> UserRedisRepositoryABC:
        ...

    @abstractmethod
    async def return_user_business_entity_postgres_repository(self, session: AsyncSession) -> UserBusinessEntityPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def return_user_business_entity_redis_repository(self, redis_client: Redis) -> UserBusinessEntityRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def return_external_business_entity_postgres_repository(self, session: AsyncSession) -> ExternalBusinessEntityPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def return_external_business_entity_redis_repository(self, redis_client: Redis) -> ExternalBusinessEntityRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def return_invoice_postgres_repository(self, session: AsyncSession) -> InvoicePostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def return_invoice_redis_repository(self, redis_client: Redis) -> InvoiceRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def return_invoice_item_postgres_repository(self, session: AsyncSession) -> InvoiceItemPostgresRepositoryABC:
        ...

    @abstractmethod
    async def return_files_repository(self) -> FilesRepositoryABC:
        ...

    @abstractmethod
    async def return_ai_extracted_invoice_postgres_repository(self, session: AsyncSession) -> AIExtractedInvoicePostgresRepositoryABC:
        ...

    @abstractmethod
    async def return_ai_extracted_invoice_item_postgres_repository(self, session: AsyncSession) -> AIExtractedInvoiceItemPostgresRepositoryABC:
        ...

    @abstractmethod
    async def return_ai_extracted_external_business_entity_postgres_repository(self, session: AsyncSession) -> AIExtractedExternalBusinessEntityPostgresRepositoryABC:
        ...

    @abstractmethod
    async def return_ai_extracted_user_business_entity_postgres_repository(self, session: AsyncSession) -> AIExtractedUserBusinessEntityPostgresRepositoryABC:
        ...

    @abstractmethod
    async def return_ai_is_external_business_recognized_postgres_repository(self, session: AsyncSession) -> AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def return_ai_is_user_business_recognized_postgres_repository(self, session: AsyncSession) -> AIIsUserBusinessRecognizedPostgresRepositoryABC:
        ...

    @abstractmethod
    async def return_ai_extraction_failure_postgres_repository(self, session: AsyncSession) -> AIExtractionFailurePostgresRepositoryABC:
        ...

    @abstractmethod
    async def return_report_postgres_repository(self, session: AsyncSession) -> ReportPostgresRepositoryABC:
        ...