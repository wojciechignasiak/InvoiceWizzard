from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.postgres.repositories.user_business_entity_repository_abc import UserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.external_business_entity_repository_abc import ExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.invoice_postgres_repository_abc import InvoicePostgresRepositoryABC
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.database.redis.repositories.user_business_entity_repository_abc import UserBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.invoice_repository_abc import InvoiceRedisRepositoryABC


class RepositoriesRegistry:
    __slots__= (
        'user_postgres_repository', 
        'user_redis_repository',
        'user_business_entity_postgres_repository',
        'user_business_entity_redis_repository',
        'external_business_entity_postgres_repository',
        'invoice_postgres_repository',
        'invoice_redis_repository',
        'invoice_item_postgres_repository'
        )

    def __init__(self, 
                user_postgres_repository: UserPostgresRepositoryABC, 
                user_redis_repository: UserRedisRepositoryABC,
                user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC,
                user_business_entity_redis_repository: UserBusinessEntityRedisRepositoryABC,
                external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC,
                invoice_postgres_repository: InvoicePostgresRepositoryABC,
                invoice_redis_repository: InvoiceRedisRepositoryABC,
                invoice_item_postgres_repository: InvoiceItemPostgresRepositoryABC) -> None:
        
        self.user_postgres_repository = user_postgres_repository
        self.user_redis_repository = user_redis_repository
        self.user_business_entity_postgres_repository = user_business_entity_postgres_repository
        self.user_business_entity_redis_repository = user_business_entity_redis_repository
        self.external_business_entity_postgres_repository = external_business_entity_postgres_repository
        self.invoice_postgres_repository = invoice_postgres_repository
        self.invoice_redis_repository = invoice_redis_repository
        self.invoice_item_postgres_repository = invoice_item_postgres_repository


    async def return_user_postgres_repository(self, session) -> UserPostgresRepositoryABC:
        return self.user_postgres_repository(session)
    
    async def return_user_redis_repository(self, redis_client) -> UserRedisRepositoryABC:
        return self.user_redis_repository(redis_client)

    async def return_user_business_entity_postgres_repository(self, session) -> UserBusinessEntityPostgresRepositoryABC:
        return self.user_business_entity_postgres_repository(session)
    
    async def return_user_business_entity_redis_repository(self, redis_client) -> UserBusinessEntityRedisRepositoryABC:
        return self.user_business_entity_redis_repository(redis_client)
    
    async def return_external_business_entity_postgres_repository(self, session) -> ExternalBusinessEntityPostgresRepositoryABC:
        return self.external_business_entity_postgres_repository(session)
    
    async def return_invoice_postgres_repository(self, session) -> InvoicePostgresRepositoryABC:
        return self.invoice_postgres_repository(session)
    
    async def return_invoice_redis_repository(self, redis_client) -> InvoiceRedisRepositoryABC:
        return self.invoice_redis_repository(redis_client)
    
    async def return_invoice_item_postgres_repository(self, session) -> InvoiceItemPostgresRepositoryABC:
        return self.invoice_item_postgres_repository(session)