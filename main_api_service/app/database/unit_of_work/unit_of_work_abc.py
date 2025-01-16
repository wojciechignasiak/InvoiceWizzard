#postgres repositories
from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.postgres.repositories.user_business_entity_repository_abc import UserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.external_business_entity_repository_abc import ExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.invoice_repository_abc import InvoicePostgresRepositoryABC
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_invoice_repository_abc import AIExtractedInvoicePostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_invoice_item_repository_abc import AIExtractedInvoiceItemPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_user_business_entity_repository_abc import AIExtractedUserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_external_business_entity_repository_abc import AIExtractedExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.ai_is_external_business_recognized_repository_abc import AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC
from app.database.postgres.repositories.ai_is_user_business_recognized_repository_abc import AIIsUserBusinessRecognizedPostgresRepositoryABC
from app.database.postgres.repositories.ai_extraction_failure_repository_abc import AIExtractionFailurePostgresRepositoryABC

#redis repositories
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.database.redis.repositories.user_business_entity_repository_abc import UserBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.external_business_entity_repository_abc import ExternalBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.invoice_repository_abc import InvoiceRedisRepositoryABC

#files repository
from app.files.files_repository_abc import FilesRepositoryABC

#1st party imports
from abc import ABC, abstractmethod
from async_property import async_property

class UnitOfWorkABC(ABC):

    
    @abstractmethod
    async def sql_commit(self):
        ...

    @abstractmethod
    async def sql_rollback(self):
        ...
    
    @abstractmethod
    async def sql_close_session(self):
        ...
    
    @async_property
    @abstractmethod
    async def user_postgres_repository(self) -> UserPostgresRepositoryABC:
        ...

    @abstractmethod
    async def user_business_entity_postgres_repository(self) -> UserBusinessEntityPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def external_business_entity_postgres_repository(self) -> ExternalBusinessEntityPostgresRepositoryABC:
        ...

    @abstractmethod
    async def invoice_postgres_repository(self) -> InvoicePostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def invoice_item_postgres_repository(self) -> InvoiceItemPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def ai_extracted_invoice_postgres_repository(self) -> AIExtractedInvoicePostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def ai_extracted_invoice_item_postgres_repository(self) -> AIExtractedInvoiceItemPostgresRepositoryABC:
        ...

    @abstractmethod
    async def ai_extracted_user_business_entity_postgres_repository(self) -> AIExtractedUserBusinessEntityPostgresRepositoryABC:
        ...

    @abstractmethod
    async def ai_extracted_external_business_entity_postgres_repository(self) -> AIExtractedExternalBusinessEntityPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def ai_is_user_business_recognized_postgres_repository(self) -> AIIsUserBusinessRecognizedPostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def ai_is_external_business_recognized_postgres_repository(self) -> AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC:
        ...

    @abstractmethod
    async def ai_extraction_failure_postgres_repository(self) -> AIExtractionFailurePostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def user_redis_repository(self) -> UserRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def user_business_entity_redis_repository(self) -> UserBusinessEntityRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def external_business_entity_redis_repository(self) -> ExternalBusinessEntityRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def invoice_redis_repository(self) -> InvoiceRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def files_repository(self) -> FilesRepositoryABC:
        ...

    
