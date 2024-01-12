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
from app.files.files_repository_abc import FilesRepositoryABC
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis



class RepositoriesRegistry(RepositoriesRegistryABC):
    __slots__= (
        'user_postgres_repository', 
        'user_redis_repository',
        'user_business_entity_postgres_repository',
        'user_business_entity_redis_repository',
        'external_business_entity_postgres_repository',
        'external_business_entity_redis_repository',
        'invoice_postgres_repository',
        'invoice_redis_repository',
        'invoice_item_postgres_repository',
        'files_repository',
        'ai_extracted_invoice_postgres_repository',
        'ai_extracted_invoice_item_postgres_repository',
        'ai_extracted_external_business_entity_postgres_repository',
        'ai_extracted_user_business_entity_postgres_repository',
        'ai_is_external_business_recognized_postgres_repository',
        'ai_is_user_business_recognized_postgres_repository'
        )

    def __init__(self, 
                user_postgres_repository: UserPostgresRepositoryABC, 
                user_redis_repository: UserRedisRepositoryABC,
                user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC,
                user_business_entity_redis_repository: UserBusinessEntityRedisRepositoryABC,
                external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC,
                external_business_entity_redis_repository: ExternalBusinessEntityRedisRepositoryABC,
                invoice_postgres_repository: InvoicePostgresRepositoryABC,
                invoice_redis_repository: InvoiceRedisRepositoryABC,
                invoice_item_postgres_repository: InvoiceItemPostgresRepositoryABC,
                files_repository: FilesRepositoryABC,
                ai_extracted_invoice_postgres_repository: AIExtractedInvoicePostgresRepositoryABC,
                ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC,
                ai_extracted_external_business_entity_postgres_repository: AIExtractedExternalBusinessEntityPostgresRepositoryABC,
                ai_extracted_user_business_entity_postgres_repository: AIExtractedUserBusinessEntityPostgresRepositoryABC,
                ai_is_external_business_recognized_postgres_repository: AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC,
                ai_is_user_business_recognized_postgres_repository: AIIsUserBusinessRecognizedPostgresRepositoryABC
                ) -> None:
        
        self.user_postgres_repository = user_postgres_repository
        self.user_redis_repository = user_redis_repository
        self.user_business_entity_postgres_repository = user_business_entity_postgres_repository
        self.user_business_entity_redis_repository = user_business_entity_redis_repository
        self.external_business_entity_postgres_repository = external_business_entity_postgres_repository
        self.external_business_entity_redis_repository = external_business_entity_redis_repository
        self.invoice_postgres_repository = invoice_postgres_repository
        self.invoice_redis_repository = invoice_redis_repository
        self.invoice_item_postgres_repository = invoice_item_postgres_repository
        self.files_repository = files_repository
        self.ai_extracted_invoice_postgres_repository = ai_extracted_invoice_postgres_repository
        self.ai_extracted_invoice_item_postgres_repository = ai_extracted_invoice_item_postgres_repository
        self.ai_extracted_external_business_entity_postgres_repository = ai_extracted_external_business_entity_postgres_repository
        self.ai_extracted_user_business_entity_postgres_repository = ai_extracted_user_business_entity_postgres_repository
        self.ai_is_external_business_recognized_postgres_repository = ai_is_external_business_recognized_postgres_repository
        self.ai_is_user_business_recognized_postgres_repository = ai_is_user_business_recognized_postgres_repository


    async def return_user_postgres_repository(self, session: AsyncSession) -> UserPostgresRepositoryABC:
        return self.user_postgres_repository(session)
    
    async def return_user_redis_repository(self, redis_client: Redis) -> UserRedisRepositoryABC:
        return self.user_redis_repository(redis_client)

    async def return_user_business_entity_postgres_repository(self, session: AsyncSession) -> UserBusinessEntityPostgresRepositoryABC:
        return self.user_business_entity_postgres_repository(session)
    
    async def return_user_business_entity_redis_repository(self, redis_client: Redis) -> UserBusinessEntityRedisRepositoryABC:
        return self.user_business_entity_redis_repository(redis_client)
    
    async def return_external_business_entity_postgres_repository(self, session: AsyncSession) -> ExternalBusinessEntityPostgresRepositoryABC:
        return self.external_business_entity_postgres_repository(session)
    
    async def return_external_business_entity_redis_repository(self, redis_client: Redis) -> ExternalBusinessEntityRedisRepositoryABC:
        return self.external_business_entity_redis_repository(redis_client)
    
    async def return_invoice_postgres_repository(self, session: AsyncSession) -> InvoicePostgresRepositoryABC:
        return self.invoice_postgres_repository(session)
    
    async def return_invoice_redis_repository(self, redis_client: Redis) -> InvoiceRedisRepositoryABC:
        return self.invoice_redis_repository(redis_client)
    
    async def return_invoice_item_postgres_repository(self, session: AsyncSession) -> InvoiceItemPostgresRepositoryABC:
        return self.invoice_item_postgres_repository(session)
    
    async def return_files_repository(self) -> FilesRepositoryABC:
        return self.files_repository
    
    async def return_ai_extracted_invoice_postgres_repository(self, session: AsyncSession) -> AIExtractedInvoicePostgresRepositoryABC:
        return self.ai_extracted_invoice_postgres_repository(session)
    
    async def return_ai_extracted_invoice_item_postgres_repository(self, session: AsyncSession) -> AIExtractedInvoiceItemPostgresRepositoryABC:
        return self.ai_extracted_invoice_item_postgres_repository(session)
    
    async def return_ai_extracted_external_business_entity_postgres_repository(self, session: AsyncSession) -> AIExtractedExternalBusinessEntityPostgresRepositoryABC:
        return self.ai_extracted_external_business_entity_postgres_repository(session)
    
    async def return_ai_extracted_user_business_entity_postgres_repository(self, session: AsyncSession) -> AIExtractedUserBusinessEntityPostgresRepositoryABC:
        return self.ai_extracted_user_business_entity_postgres_repository(session)
    
    async def return_ai_is_external_business_recognized_postgres_repository(self, session: AsyncSession) -> AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC:
        return self.ai_is_external_business_recognized_postgres_repository(session)
    
    async def return_ai_is_user_business_recognized_postgres_repository(self, session: AsyncSession) -> AIIsUserBusinessRecognizedPostgresRepositoryABC:
        return self.ai_is_user_business_recognized_postgres_repository(session)