import os
import redis
import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette import middleware
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from kafka.errors import KafkaTimeoutError, KafkaError
from aiokafka import AIOKafkaProducer
from app.kafka.initialize_topics.startup_topics import startup_topics
from contextlib import asynccontextmanager
from app.schema.schema import Base
from app.database.repositories_registry import RepositoriesRegistry
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.database.postgres.repositories.user_business_entity_repository import UserBusinessEntityPostgresRepository
from app.database.redis.repositories.user_business_entity_repository import UserBusinessEntityRedisRepository
from app.database.postgres.repositories.external_business_entity_repository import ExternalBusinessEntityPostgresRepository
from app.database.postgres.repositories.invoice_postgres_repository import InvoicePostgresRepository
from app.database.redis.repositories.invoice_repository import InvoiceRedisRepository
from app.database.postgres.repositories.invoice_item_repository import InvoiceItemPostgresRepository
from app.routers import (
    user_router,
    user_business_entity_router,
    external_business_entity_router
    )


middleware = [
    middleware.Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods="*",
        allow_headers=["*"]
    )]

POSTGRES_USERNAME = os.environ.get("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB = os.environ.get("POSTGRES_DB")

POSTGRES_URL = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

KAFKA_HOST = os.environ.get("KAFKA_HOST")
KAFKA_PORT = os.environ.get("KAFKA_PORT")
KAFKA_URL = f"{KAFKA_HOST}:{KAFKA_PORT}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' Run at startup
        Initialise databases clients.
    '''
    while True:
        try:
            print("Creating PostgreSQL engine...")
            app.state.engine: AsyncEngine = create_async_engine(
                                POSTGRES_URL,
                                echo=False,
                                future=True
                            )
            print("Testing connection to PostgreSQL...")
            async with app.state.engine.connect() as connection:
                result = await connection.execute(text("SELECT current_user;"))
                current_user = result.scalar()

            if current_user == POSTGRES_USERNAME:
                print('Connection to PostgreSQL status: Connected')
            else:
                print('Connection to PostgreSQL status: Failed. Retrying...')
                raise SQLAlchemyError
            break
        except SQLAlchemyError:
            await asyncio.sleep(3)

    async with app.state.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    while True:
        try:
            print("Creating Redis client...")
            app.state.redis_client: redis.Redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
            print("Testing connection to Redis...")
            redis_info = app.state.redis_client.ping()
            if redis_info:
                print('Connection to Redis status: Connected')
            else:
                print('Connection to Redis status: Failed. Retrying...')
                raise ConnectionError
            break
        except ConnectionError:
            await asyncio.sleep(3)

    while True:
        try:
            print("Initializing Kafka topics...")
            await startup_topics(KAFKA_URL)
            print("Kafka topics initialized!")
            break
        except KafkaTimeoutError as e:
            print(f'Kafka Timeout error durning topic initialization: {e}')
        except KafkaError as e:
            print(f'Kafka error durning topic initalization: {e}')

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
            app.state.repositories_registry = repositories_registry
            print("Repositories registry initialized!")
            break
        except Exception as e:
            print(f'Error occured durning initializing repositories registry: {e}')

    while True:
        try:
            print("Running Kafka Producer on separate event loop...")
            loop = asyncio.get_event_loop()
            app.state.kafka_producer: AIOKafkaProducer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_URL)
            await app.state.kafka_producer.start()
            print("Kafka Producer started...")
            break
        except (KafkaError, KafkaTimeoutError) as e:
            print(f'Error occured durning running Kafka Producer: {e}')

    yield
    ''' Run on shutdown
        Close the connection
        Clear variables and release the resources
    '''
    print("Disposing PostgreSQL engine...")
    await app.state.engine.dispose()
    print("Stopping Kafka producer...")
    await app.state.kafka_producer.stop()
    

def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan, openapi_url="/openapi.json", docs_url="/docs", middleware=middleware)
    application.include_router(user_router.router, tags=["user"])
    application.include_router(user_business_entity_router.router, tags=["user-business-entity"])
    application.include_router(external_business_entity_router.router, tags=["external-business-entity"])
    return application

app = create_application()