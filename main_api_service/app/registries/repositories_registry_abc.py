from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.postgres.repositories.user_business_entity_repository_abc import UserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.external_business_entity_repository_abc import ExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.invoice_repository_abc import InvoicePostgresRepositoryABC
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_external_business_entity_repository_abc import AIExtractedExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_invoice_item_repository_abc import AIExtractedInvoiceItemPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_invoice_repository_abc import AIExtractedInvoicePostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_user_business_entity_repository_abc import AIExtractedUserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.ai_is_external_business_recognized_repository_abc import AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC
from app.database.postgres.repositories.ai_is_user_business_recognized_repository_abc import AIIsUserBusinessRecognizedPostgresRepositoryABC
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.database.redis.repositories.user_business_entity_repository_abc import UserBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.external_business_entity_repository_abc import ExternalBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.invoice_repository_abc import InvoiceRedisRepositoryABC
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from abc import ABC, abstractmethod
from app.files.files_repository_abc import FilesRepositoryABC


class RepositoriesRegistryABC(ABC):

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