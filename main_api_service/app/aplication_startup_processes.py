import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from redis.asyncio import Redis, BlockingConnectionPool
from aiokafka.errors import KafkaTimeoutError, KafkaError
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.kafka.initialize_topics.startup_topics import startup_topics
from app.factories.repositories_factory import RepositoriesFactory
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.postgres.repositories.user_business_entity_repository import UserBusinessEntityPostgresRepository
from app.database.redis.repositories.user_business_entity_repository import UserBusinessEntityRedisRepository
from app.database.postgres.repositories.external_business_entity_repository import ExternalBusinessEntityPostgresRepository
from app.database.redis.repositories.external_business_entity_repository import ExternalBusinessEntityRedisRepository
from app.database.postgres.repositories.invoice_repository import InvoicePostgresRepository
from app.database.redis.repositories.invoice_repository import InvoiceRedisRepository
from app.database.postgres.repositories.invoice_item_repository import InvoiceItemPostgresRepository
from app.database.postgres.repositories.ai_extracted_invoice_repository import AIExtractedInvoicePostgresRepository
from app.database.postgres.repositories.ai_extracted_invoice_item_repository import AIExtractedInvoiceItemPostgresRepository
from app.database.postgres.repositories.ai_extracted_external_business_entity_repository import AIExtractedExternalBusinessEntityPostgresRepository
from app.database.postgres.repositories.ai_extracted_user_business_entity_repository import AIExtractedUserBusinessEntityPostgresRepository
from app.database.postgres.repositories.ai_is_external_business_recognized_repository import AIIsExternalBusinessEntityRecognizedPostgresRepository
from app.database.postgres.repositories.ai_is_user_business_recognized_repository import AIIsUserBusinessRecognizedPostgresRepository
from app.database.postgres.repositories.ai_extraction_failure_repository import AIExtractionFailurePostgresRepository
from app.database.postgres.repositories.report_repository import ReportPostgresRepository
from app.factories.events_factory import EventsFactory
from app.kafka.events.user_events import UserEvents
from app.kafka.events.user_business_entity_events import UserBusinessEntityEvents
from app.kafka.events.external_business_entity_events import ExternalBusinessEntityEvents
from app.kafka.events.invoice_events import InvoiceEvents
from app.kafka.events.ai_invoice_events import AIInvoiceEvents
from app.files.files_repository import FilesRepository
from app.factories.services_factory import ServicesFactory
from app.services.auth_service import AuthService
from app.services.user_service import UserService

class ApplicationStartupProcesses:

    __slots__= (
        '__postgres_username', 
        '__postgres_password',
        '__postgres_host',
        '__postgres_port',
        '__postgres_db',
        '__postgres_url',
        '__redis_password',
        '__redis_host',
        '__redis_port',
        '__kafka_host',
        '__kafka_port',
        '__kafka_url',
        )

    def __init__(self) -> None:
        
        self.__postgres_username = os.environ.get("POSTGRES_USERNAME")
        self.__postgres_password = os.environ.get("POSTGRES_PASSWORD")
        self.__postgres_host = os.environ.get("POSTGRES_HOST")
        self.__postgres_port = os.environ.get("POSTGRES_PORT")
        self.__postgres_db = os.environ.get("POSTGRES_DB")
        self.__postgres_url = f"postgresql+asyncpg://{self.__postgres_username}:{self.__postgres_password}@{self.__postgres_host}:{self.__postgres_port}/{self.__postgres_db}"

        self.__redis_password = os.environ.get("REDIS_PASSWORD")
        self.__redis_host = os.environ.get("REDIS_HOST")
        self.__redis_port = os.environ.get("REDIS_PORT")

        self.__kafka_host = os.environ.get("KAFKA_HOST")
        self.__kafka_port = os.environ.get("KAFKA_PORT")
        self.__kafka_url = f"{self.__kafka_host}:{self.__kafka_port}"

    async def postgres_engine(self) -> AsyncEngine:
        while True:
            try:
                print("Creating PostgreSQL engine...")
                engine: AsyncEngine = create_async_engine(
                                    self.__postgres_url,
                                    echo=False,
                                    future=True
                                )
                print("Testing connection to PostgreSQL...")
                async with engine.connect() as connection:
                    result = await connection.execute(text("SELECT current_user;"))
                    current_user = result.scalar()

                if current_user == self.__postgres_username:
                    print('Connection to PostgreSQL status: Connected')
                else:
                    print('Connection to PostgreSQL status: Failed. Retrying...')
                    raise SQLAlchemyError
                return engine
            except SQLAlchemyError:
                await asyncio.sleep(3)

    async def redis_pool(self) -> BlockingConnectionPool:
        while True:
            try:
                print("Creating Redis connection pool...")
                redis_pool = BlockingConnectionPool(max_connections=3000, host=self.__redis_host, port=self.__redis_port, password=self.__redis_password)
                redis_client: Redis = await Redis(connection_pool=redis_pool)
                print("Testing connection to Redis...")
                redis_info = await redis_client.ping()
                if redis_info:
                    print('Connection to Redis status: Connected')
                    
                else:
                    print('Connection to Redis status: Failed. Retrying...')
                    raise ConnectionError
                return redis_pool
            except ConnectionError:
                await redis_client.close()
                await asyncio.sleep(3)

    async def kafka_topics_initialization(self):
        while True:
            try:
                print("Initializing Kafka topics...")
                await startup_topics(self.__kafka_url)
                print("Kafka topics initialized!")
                break
            except KafkaTimeoutError as e:
                print(f'Kafka Timeout error durning topic initialization: {e}')
            except KafkaError as e:
                print(f'Kafka error durning topic initalization: {e}')

    async def kafka_producer(self) -> AIOKafkaProducer:
        while True:
            try:
                print("Running Kafka Producer on separate event loop...")
                loop = asyncio.get_event_loop()
                kafka_producer: AIOKafkaProducer = AIOKafkaProducer(
                    loop=loop, 
                    bootstrap_servers=self.__kafka_url)
                return kafka_producer
            except (KafkaError, KafkaTimeoutError) as e:
                print(f'Error occured durning running Kafka Producer: {e}')

    async def kafka_consumer(self) -> AIOKafkaConsumer:
        while True:
            try:
                print("Running Kafka Consumer on separate event loop...")
                loop = asyncio.get_event_loop()
                kafka_consumer: AIOKafkaConsumer = AIOKafkaConsumer(
                    KafkaTopicsEnum.unable_to_extract_invoice_data.value, 
                    KafkaTopicsEnum.extracted_invoice_data.value,
                    loop=loop, 
                    bootstrap_servers=self.__kafka_url)
                return kafka_consumer
            except (KafkaError, KafkaTimeoutError) as e:
                print(f'Error occured durning running Kafka Consumer: {e}')

    async def repositories_factory(self) -> RepositoriesFactory:
        while True:
            try:
                print("Initializing repositories factory...")
                repositories_factory: RepositoriesFactory = RepositoriesFactory(
                    UserPostgresRepository, 
                    UserRedisRepository, 
                    UserBusinessEntityPostgresRepository,
                    UserBusinessEntityRedisRepository,
                    ExternalBusinessEntityPostgresRepository,
                    ExternalBusinessEntityRedisRepository,
                    InvoicePostgresRepository,
                    InvoiceRedisRepository,
                    InvoiceItemPostgresRepository,
                    FilesRepository,
                    AIExtractedInvoicePostgresRepository,
                    AIExtractedInvoiceItemPostgresRepository,
                    AIExtractedExternalBusinessEntityPostgresRepository,
                    AIExtractedUserBusinessEntityPostgresRepository,
                    AIIsExternalBusinessEntityRecognizedPostgresRepository,
                    AIIsUserBusinessRecognizedPostgresRepository,
                    AIExtractionFailurePostgresRepository,
                    ReportPostgresRepository
                    )
                
                print("Repositories factory initialized!")
                return repositories_factory
            except Exception as e:
                print(f'Error occured durning initializing repositories factory: {e}')

    async def services_factory(self) -> ServicesFactory:
        while True:
            try:
                print("Initializing services factory...")
                services_factory: ServicesFactory = ServicesFactory(
                    AuthService,
                    UserService
                    )
                print("Services factory initialized!")
                return services_factory
            except Exception as e:
                print(f'Error occured durning initializing services factory: {e}')

    async def events_factory(self) -> EventsFactory:
        while True:
            try:
                print("Initializing events factory...")
                events_registry: EventsFactory = EventsFactory(
                    UserEvents,
                    UserBusinessEntityEvents,
                    ExternalBusinessEntityEvents,
                    InvoiceEvents,
                    AIInvoiceEvents
                    )
                print("Events registry initialized!")
                return events_registry
            except Exception as e:
                print(f'Error occured durning initializing events factory: {e}')