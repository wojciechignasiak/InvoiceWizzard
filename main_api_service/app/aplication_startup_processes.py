import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import redis
from kafka.errors import KafkaTimeoutError, KafkaError
from aiokafka import AIOKafkaProducer
from app.kafka.initialize_topics.startup_topics import startup_topics
from app.registries.repositories_registry import RepositoriesRegistry
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.postgres.repositories.user_business_entity_repository import UserBusinessEntityPostgresRepository
from app.database.redis.repositories.user_business_entity_repository import UserBusinessEntityRedisRepository
from app.database.postgres.repositories.external_business_entity_repository import ExternalBusinessEntityPostgresRepository
from app.database.postgres.repositories.invoice_repository import InvoicePostgresRepository
from app.database.redis.repositories.invoice_repository import InvoiceRedisRepository
from app.database.postgres.repositories.invoice_item_repository import InvoiceItemPostgresRepository
from app.registries.events_registry import EventsRegistry
from app.kafka.events.user_events import UserEvents
from app.kafka.events.user_business_entity_events import UserBusinessEntityEvents

class ApplicationStartupProcesses:

    def __init__(self) -> None:
        
        self.postgres_username = os.environ.get("POSTGRES_USERNAME")
        self.postgres_password = os.environ.get("POSTGRES_PASSWORD")
        self.postgres_host = os.environ.get("POSTGRES_HOST")
        self.postgres_port = os.environ.get("POSTGRES_PORT")
        self.postgres_db = os.environ.get("POSTGRES_DB")
        self.postgres_url = f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

        self.redis_password = os.environ.get("REDIS_PASSWORD")
        self.redis_host = os.environ.get("REDIS_HOST")
        self.redis_port = os.environ.get("REDIS_PORT")

        self.kafka_host = os.environ.get("KAFKA_HOST")
        self.kafka_port = os.environ.get("KAFKA_PORT")
        self.kafka_url = f"{self.kafka_host}:{self.kafka_port}"

    async def postgres_engine(self) -> AsyncEngine:
        while True:
            try:
                print("Creating PostgreSQL engine...")
                engine: AsyncEngine = create_async_engine(
                                    self.postgres_url,
                                    echo=False,
                                    future=True
                                )
                print("Testing connection to PostgreSQL...")
                async with engine.connect() as connection:
                    result = await connection.execute(text("SELECT current_user;"))
                    current_user = result.scalar()

                if current_user == self.postgres_username:
                    print('Connection to PostgreSQL status: Connected')
                else:
                    print('Connection to PostgreSQL status: Failed. Retrying...')
                    raise SQLAlchemyError
                return engine
            except SQLAlchemyError:
                await asyncio.sleep(3)

    async def redis_client(self) -> redis.Redis:
        while True:
            try:
                print("Creating Redis client...")
                redis_client: redis.Redis = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
                print("Testing connection to Redis...")
                redis_info = redis_client.ping()
                if redis_info:
                    print('Connection to Redis status: Connected')
                else:
                    print('Connection to Redis status: Failed. Retrying...')
                    raise ConnectionError
                return redis_client
            except ConnectionError:
                await asyncio.sleep(3)

    async def kafka_topics_initialization(self):
        while True:
            try:
                print("Initializing Kafka topics...")
                await startup_topics(self.kafka_url)
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
                kafka_producer: AIOKafkaProducer = AIOKafkaProducer(loop=loop, bootstrap_servers=self.kafka_url)
                return kafka_producer
            except (KafkaError, KafkaTimeoutError) as e:
                print(f'Error occured durning running Kafka Producer: {e}')

    async def repositories_registry(self) -> RepositoriesRegistry:
        while True:
            try:
                print("Initializing repositories registry...")
                repositories_registry: RepositoriesRegistry = RepositoriesRegistry(
                    UserPostgresRepository, 
                    UserRedisRepository, 
                    UserBusinessEntityPostgresRepository,
                    UserBusinessEntityRedisRepository,
                    ExternalBusinessEntityPostgresRepository,
                    InvoicePostgresRepository,
                    InvoiceRedisRepository,
                    InvoiceItemPostgresRepository
                    )
                
                print("Repositories registry initialized!")
                return repositories_registry
            except Exception as e:
                print(f'Error occured durning initializing repositories registry: {e}')

    async def events_registry(self) -> EventsRegistry:
        while True:
            try:
                print("Initializing events registry...")
                events_registry: EventsRegistry = EventsRegistry(
                    UserEvents,
                    UserBusinessEntityEvents
                    )
                print("Events registry initialized!")
                return events_registry
            except Exception as e:
                print(f'Error occured durning initializing events registry: {e}')