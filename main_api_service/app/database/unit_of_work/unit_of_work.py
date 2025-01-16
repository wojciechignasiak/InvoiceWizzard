#postgres repositories
from app.database.postgres.repositories.user_repository_abc import UserPostgresRepositoryABC
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.postgres.repositories.user_business_entity_repository_abc import UserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.user_business_entity_repository import UserBusinessEntityPostgresRepository
from app.database.postgres.repositories.external_business_entity_repository_abc import ExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.external_business_entity_repository import ExternalBusinessEntityPostgresRepository
from app.database.postgres.repositories.invoice_repository_abc import InvoicePostgresRepositoryABC
from app.database.postgres.repositories.invoice_repository import InvoicePostgresRepository
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.database.postgres.repositories.invoice_item_repository import InvoiceItemPostgresRepository
from app.database.postgres.repositories.ai_extracted_invoice_repository_abc import AIExtractedInvoicePostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_invoice_repository import AIExtractedInvoicePostgresRepository
from app.database.postgres.repositories.ai_extracted_invoice_item_repository_abc import AIExtractedInvoiceItemPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_invoice_item_repository import AIExtractedInvoiceItemPostgresRepository
from app.database.postgres.repositories.ai_extracted_user_business_entity_repository_abc import AIExtractedUserBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_user_business_entity_repository import AIExtractedUserBusinessEntityPostgresRepository
from app.database.postgres.repositories.ai_extracted_external_business_entity_repository_abc import AIExtractedExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.ai_extracted_external_business_entity_repository import AIExtractedExternalBusinessEntityPostgresRepository
from app.database.postgres.repositories.ai_is_external_business_recognized_repository_abc import AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC
from app.database.postgres.repositories.ai_is_external_business_recognized_repository import AIIsExternalBusinessEntityRecognizedPostgresRepository
from app.database.postgres.repositories.ai_is_user_business_recognized_repository_abc import AIIsUserBusinessRecognizedPostgresRepositoryABC
from app.database.postgres.repositories.ai_is_user_business_recognized_repository import AIIsUserBusinessRecognizedPostgresRepository
from app.database.postgres.repositories.ai_extraction_failure_repository_abc import AIExtractionFailurePostgresRepositoryABC
from app.database.postgres.repositories.ai_extraction_failure_repository import AIExtractionFailurePostgresRepository

#redis repositories
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.redis.repositories.user_business_entity_repository_abc import UserBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.user_business_entity_repository import UserBusinessEntityRedisRepository
from app.database.redis.repositories.external_business_entity_repository_abc import ExternalBusinessEntityRedisRepositoryABC
from app.database.redis.repositories.external_business_entity_repository import ExternalBusinessEntityRedisRepository
from app.database.redis.repositories.invoice_repository_abc import InvoiceRedisRepositoryABC
from app.database.redis.repositories.invoice_repository import InvoiceRedisRepository

#files repository
from app.files.files_repository_abc import FilesRepositoryABC
from app.files.files_repository import FilesRepository

#3rd party libraries import
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis import Redis, BlockingConnectionPool

class UnitOfWork():
    __slots__ = (
        '_sql_engine',
        '_sql_session',
        '_user_postgres_repository', 
        '_user_business_entity_postgres_repository',
        '_external_business_entity_postgres_repository',
        '_invoice_postgres_repository',
        '_invoice_item_postgres_repository',
        '_ai_extracted_invoice_postgres_repository',
        '_ai_extracted_invoice_item_postgres_repository',
        '_ai_extracted_user_business_entity_postgres_repository',
        '_ai_extracted_external_business_entity_postgres_repository',
        '_ai_is_user_business_recognized_postgres_repository',
        '_ai_is_external_business_recognized_postgres_repository',
        '_ai_extraction_failure_postgres_repository',
        '_redis_pool',
        '_redis_client',
        '_user_redis_repository',
        '_user_business_entity_redis_repository',
        '_external_business_entity_redis_repository',
        '_invoice_redis_repository',
        '_files_repository',

        )
    
    def __init__(self, request: Request):
        self._sql_engine: AsyncEngine = request.app.state.engine
        self._sql_session: AsyncSession = self.__sql_get_session()
        self._user_postgres_repository: UserPostgresRepositoryABC | None = None
        self._user_business_entity_postgres_repository: UserBusinessEntityPostgresRepositoryABC | None = None
        self._external_business_entity_postgres_repository: ExternalBusinessEntityPostgresRepositoryABC | None = None
        self._invoice_postgres_repository: InvoicePostgresRepositoryABC | None = None
        self._invoice_item_postgres_repository: InvoiceItemPostgresRepositoryABC | None = None
        self._ai_extracted_invoice_postgres_repository: AIExtractedInvoicePostgresRepositoryABC | None = None
        self._ai_extracted_invoice_item_postgres_repository: AIExtractedInvoiceItemPostgresRepositoryABC | None = None
        self._ai_extracted_user_business_entity_postgres_repository: AIExtractedUserBusinessEntityPostgresRepositoryABC | None = None
        self._ai_extracted_external_business_entity_postgres_repository: AIExtractedExternalBusinessEntityPostgresRepositoryABC | None = None
        self._ai_is_user_business_recognized_postgres_repository: AIIsUserBusinessRecognizedPostgresRepositoryABC | None = None
        self._ai_is_external_business_recognized_postgres_repository: AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC | None = None
        self._ai_extraction_failure_postgres_repository: AIExtractionFailurePostgresRepositoryABC | None = None
        self._redis_pool: BlockingConnectionPool = request.app.state.redis_pool
        self._redis_client: Redis = self.__redis_get_client()
        self._user_redis_repository: UserRedisRepositoryABC | None = None
        self._user_business_entity_redis_repository: UserBusinessEntityRedisRepositoryABC | None = None
        self._external_business_entity_redis_repository: ExternalBusinessEntityRedisRepositoryABC | None = None
        self._invoice_redis_repository: InvoiceRedisRepositoryABC | None = None
        self._files_repository: FilesRepositoryABC | None = None


    async def __redis_get_client(self):
        self._redis_client: Redis = Redis(connection_pool=self._redis_pool, decode_responses=True)

    async def __sql_get_session(self):
        self._sql_session: AsyncSession = async_sessionmaker(self._sql_engine, expire_on_commit=False, class_=AsyncSession)
    
    async def sql_commit(self):
        if self._sql_session:
            self._sql_session.commit()
            self._sql_session: None = None

    async def sql_rollback(self):
        if self._sql_session:
            self._sql_session.rollback()
            self._sql_session: None = None
    
    async def sql_close_session(self):
        if self._sql_session:
            self._sql_session.aclose()
            self._sql_session: None = None

    async def user_postgres_repository(self) -> UserPostgresRepositoryABC:
        if not self._sql_session:
            self.__sql_get_session()
        if not self._user_postgres_repository:
            self._user_postgres_repository = UserPostgresRepository(self._sql_session)
        return self._user_postgres_repository
    
    async def user_business_entity_postgres_repository(self) -> UserBusinessEntityPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._user_business_entity_postgres_repository:
            self._user_business_entity_postgres_repository = UserBusinessEntityPostgresRepository(self._sql_session)
        return self._user_business_entity_postgres_repository

    async def external_business_entity_postgres_repository(self) -> ExternalBusinessEntityPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._external_business_entity_postgres_repository:
            self._external_business_entity_postgres_repository = ExternalBusinessEntityPostgresRepository(self._sql_session)
        return self._external_business_entity_postgres_repository

    async def invoice_postgres_repository(self) -> InvoicePostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._invoice_postgres_repository:
            self._invoice_postgres_repository = InvoicePostgresRepository(self._sql_session)
        return self._invoice_postgres_repository

    async def invoice_item_postgres_repository(self) -> InvoiceItemPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._invoice_item_postgres_repository:
            self._invoice_item_postgres_repository = InvoiceItemPostgresRepository(self._sql_session)
        return self._invoice_item_postgres_repository

    async def ai_extracted_invoice_postgres_repository(self) -> AIExtractedInvoicePostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._ai_extracted_invoice_postgres_repository:
            self._ai_extracted_invoice_postgres_repository = AIExtractedInvoicePostgresRepository(self._sql_session)
        return self._ai_extracted_invoice_postgres_repository

    async def ai_extracted_invoice_item_postgres_repository(self) -> AIExtractedInvoiceItemPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._ai_extracted_invoice_item_postgres_repository:
            self._ai_extracted_invoice_item_postgres_repository = AIExtractedInvoiceItemPostgresRepository(self._sql_session)
        return self._ai_extracted_invoice_item_postgres_repository

    async def ai_extracted_user_business_entity_postgres_repository(self) -> AIExtractedUserBusinessEntityPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._ai_extracted_user_business_entity_postgres_repository:
            self._ai_extracted_user_business_entity_postgres_repository = AIExtractedUserBusinessEntityPostgresRepository(self._sql_session)
        return self._ai_extracted_user_business_entity_postgres_repository

    async def ai_extracted_external_business_entity_postgres_repository(self) -> AIExtractedExternalBusinessEntityPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._ai_extracted_external_business_entity_postgres_repository:
            self._ai_extracted_external_business_entity_postgres_repository = AIExtractedExternalBusinessEntityPostgresRepository(self._sql_session)
        return self._ai_extracted_external_business_entity_postgres_repository

    async def ai_is_user_business_recognized_postgres_repository(self) -> AIIsUserBusinessRecognizedPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._ai_is_user_business_recognized_postgres_repository:
            self._ai_is_user_business_recognized_postgres_repository = AIIsUserBusinessRecognizedPostgresRepository(self._sql_session)
        return self._ai_is_user_business_recognized_postgres_repository

    async def ai_is_external_business_recognized_postgres_repository(self) -> AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._ai_is_external_business_recognized_postgres_repository:
            self._ai_is_external_business_recognized_postgres_repository = AIIsExternalBusinessEntityRecognizedPostgresRepository(self._sql_session)
        return self._ai_is_external_business_recognized_postgres_repository

    async def ai_extraction_failure_postgres_repository(self) -> AIExtractionFailurePostgresRepositoryABC:
        if not self._sql_session:
            await self.__sql_get_session()
        if not self._ai_extraction_failure_postgres_repository:
            self._ai_extraction_failure_postgres_repository = AIExtractionFailurePostgresRepository(self._sql_session)
        return self._ai_extraction_failure_postgres_repository

    async def user_redis_repository(self) -> UserRedisRepositoryABC:
        if not self._redis_client:
            await self.__redis_get_client()
        if not self._user_redis_repository:
            self._user_redis_repository = UserRedisRepository(self._redis_client)
        return self._user_redis_repository

    async def user_business_entity_redis_repository(self) -> UserBusinessEntityRedisRepositoryABC:
        if not self._redis_client:
            await self.__redis_get_client()
        if not self._user_business_entity_redis_repository:
            self._user_business_entity_redis_repository = UserBusinessEntityRedisRepository(self._redis_client)
        return self._user_business_entity_redis_repository

    async def external_business_entity_redis_repository(self) -> ExternalBusinessEntityRedisRepositoryABC:
        if not self._redis_client:
            await self.__redis_get_client()
        if not self._external_business_entity_redis_repository:
            self._external_business_entity_redis_repository = ExternalBusinessEntityRedisRepository(self._redis_client)
        return self._external_business_entity_redis_repository

    async def invoice_redis_repository(self) -> InvoiceRedisRepositoryABC:
        if not self._redis_client:
            await self.__redis_get_client()
        if not self._invoice_redis_repository:
            self._invoice_redis_repository = InvoiceRedisRepository(self._redis_client)
        return self._invoice_redis_repository

    async def files_repository(self) -> FilesRepositoryABC:
        if not self._files_repository:
            self._files_repository = FilesRepository()
        return self._files_repository