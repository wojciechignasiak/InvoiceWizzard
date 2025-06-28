from fastapi import FastAPI
from redis import BlockingConnectionPool
from starlette.middleware.cors import CORSMiddleware
from starlette import middleware
from starlette.datastructures import State
from main_api_service.app.aplication_startup_processes import ApplicationStartupProcesses
from main_api_service.app.kafka.consumed_events_managers.extracted_invoice_data_event_manager import ExtractedInvoiceDataMenager
from main_api_service.app.kafka.consumed_events_managers.extracted_invoice_data_event_manager_abc import ExtractedInvoiceDataMenagerABC
from main_api_service.app.kafka.consumed_events_managers.ai_extraction_failure_manager import AIExtractionFailureManager
from main_api_service.app.kafka.consumed_events_managers.ai_extraction_failure_manager_abc import AIExtractionFailureManagerABC
from main_api_service.app.kafka.clients.events_consumer import EventsConsumer
from contextlib import asynccontextmanager
import asyncio
from main_api_service.app.routers import (
    user_router,
    user_business_entity_router,
    external_business_entity_router,
    invoice_router,
    invoice_item_router,
    ai_extracted_invoice_router,
    ai_extracted_invoice_item_router,
    ai_extracted_external_business_entity_router,
    ai_extracted_user_business_entity_router,
    ai_is_user_business_entity_recognized_router,
    ai_is_external_business_entity_recognized_router,
    ai_extraction_failure_router,
    report_router
    )
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import BlockingConnectionPool
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

middleware = [
    middleware.Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods="*",
        allow_headers=["*"]
    )]


@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' Run at startup
        Initialise databases clients.
    '''

    app.state.engine: AsyncEngine = create_async_engine(
        f"postgresql+asyncpg://{os.environ.get("POSTGRES_USERNAME")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}",
        echo=False,
        future=True
    )

    app.state.redis_pool: BlockingConnectionPool = BlockingConnectionPool(
        max_connections=3000,
        host=os.environ.get("REDIS_HOST"),
        port=os.environ.get("REDIS_PORT"),
        password=os.environ.get("REDIS_PASSWORD")
    )

    app.state.kafka_producer: AIOKafkaProducer = AIOKafkaProducer(
        loop=asyncio.get_event_loop(),
        bootstrap_servers=f"{os.environ.get("KAFKA_HOST")}:{os.environ.get("KAFKA_PORT")}"
    )

    await app.state.kafka_producer.start()



    print("Kafka Producer started...")

    app.state.repositories_registry = await application_startup_processes.repositories_registry()

    app.state.events_registry = await application_startup_processes.events_registry()

    app.state.kafka_consumer: AIOKafkaConsumer = AIOKafkaConsumer(
                    KafkaTopicsEnum.unable_to_extract_invoice_data.value,
                    KafkaTopicsEnum.extracted_invoice_data.value,
                    loop=loop,
                    bootstrap_servers=self.kafka_url)
    
    # extracted_invoice_data_manager: ExtractedInvoiceDataMenagerABC = ExtractedInvoiceDataMenager(
    #     repositories_registry=app.state.repositories_registry,
    #     postgres_url=application_startup_processes.postgres_url)
    #
    # # ai_extraction_failure_manager: AIExtractionFailureManagerABC = AIExtractionFailureManager(
    # #     repositories_registry=app.state.repositories_registry,
    # #     postgres_url=application_startup_processes.postgres_url)
    #
    # events_consumer: EventsConsumer = EventsConsumer(
    #     kafka_consumer=app.state.kafka_consumer,
    #     extracted_invoice_data_event_manager=extracted_invoice_data_manager,
    #     ai_extraction_failure_manager=ai_extraction_failure_manager)
    #
    # asyncio.run(events_consumer.run_consumer())
    
    print("Kafka Consumer started...")

    yield
    ''' Run on shutdown
        Close the connection
        Clear variables and release the resources
    '''
    print("Disposing PostgreSQL engine...")
    await app.state.engine.dispose()
    print("Stopping Kafka Producer...")
    await app.state.kafka_producer.stop()
    print("Stopping Kafka Consumer...")
    await app.state.kafka_consumer.stop()

def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan, openapi_url="/openapi.json", docs_url="/docs", middleware=middleware)
    application.include_router(user_router.router, tags=["user"])
    application.include_router(user_business_entity_router.router, tags=["user-business-entity"])
    application.include_router(external_business_entity_router.router, tags=["external-business-entity"])
    application.include_router(invoice_router.router, tags=["invoice"])
    application.include_router(invoice_item_router.router, tags=["invoice-item"])
    application.include_router(ai_extracted_invoice_router.router, tags=["ai-extracted-invoice"])
    application.include_router(ai_extracted_invoice_item_router.router, tags=["ai-extracted-invoice-item"])
    application.include_router(ai_extracted_user_business_entity_router.router, tags=["ai-extracted-user-business-entity"])
    application.include_router(ai_is_user_business_entity_recognized_router.router, tags=["ai-is-user-business-entity-recognized"])
    application.include_router(ai_extracted_external_business_entity_router.router, tags=["ai-extracted-external-business-entity"])
    application.include_router(ai_is_external_business_entity_recognized_router.router, tags=["ai-is-external-business-entity-recognized"])
    application.include_router(ai_extraction_failure_router.router, tags=["ai-extraction-failure"])
    application.include_router(report_router.router, tags=["report"])
    return application

app = create_application()