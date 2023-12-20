from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.postgres.repositories.user_business_entity_repository_abc import UserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.external_business_entity_repository_abc import ExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.invoice_repository_abc import InvoicePostgresRepositoryABC
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.database.redis.repositories.user_business_entity_repository_abc import UserBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.invoice_repository_abc import InvoiceRedisRepositoryABC
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from abc import ABC, abstractmethod


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
    async def return_invoice_postgres_repository(self, session: AsyncSession) -> InvoicePostgresRepositoryABC:
        ...
    
    @abstractmethod
    async def return_invoice_redis_repository(self, redis_client: Redis) -> InvoiceRedisRepositoryABC:
        ...
    
    @abstractmethod
    async def return_invoice_item_postgres_repository(self, session: AsyncSession) -> InvoiceItemPostgresRepositoryABC:
        ...