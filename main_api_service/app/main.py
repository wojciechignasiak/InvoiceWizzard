from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette import middleware
from app.aplication_startup_processes import ApplicationStartupProcesses
from app.kafka.consumed_events_managers.extracted_invoice_data_event_manager import ExtractedInvoiceDataMenager
from app.kafka.consumed_events_managers.extracted_invoice_data_event_manager_abc import ExtractedInvoiceDataMenagerABC
from app.kafka.consumed_events_managers.ai_extraction_failure_manager import AIExtractionFailureManager
from app.kafka.consumed_events_managers.ai_extraction_failure_manager_abc import AIExtractionFailureManagerABC
from app.kafka.clients.events_consumer import EventsConsumer
from contextlib import asynccontextmanager
import asyncio
from app.routers import (
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
    application_statup_processes: ApplicationStartupProcesses = ApplicationStartupProcesses()

    app.state.engine = await application_statup_processes.postgres_engine()

    await application_statup_processes.kafka_topics_initialization()

    app.state.redis_pool = await application_statup_processes.redis_pool()

    await application_statup_processes.kafka_topics_initialization()

    app.state.kafka_producer = await application_statup_processes.kafka_producer()
    await app.state.kafka_producer.start()
    print("Kafka Producer started...")

    app.state.repositories_registry = await application_statup_processes.repositories_registry()

    app.state.events_registry = await application_statup_processes.events_registry()

    app.state.kafka_consumer = await application_statup_processes.kafka_consumer()
    
    extracted_invoice_data_manager: ExtractedInvoiceDataMenagerABC = ExtractedInvoiceDataMenager(
        repositories_registry=app.state.repositories_registry,
        postgres_url=application_statup_processes.postgres_url)
    
    ai_extraction_failure_manager: AIExtractionFailureManagerABC = AIExtractionFailureManager(
        repositories_registry=app.state.repositories_registry,
        postgres_url=application_statup_processes.postgres_url)
    
    events_consumer: EventsConsumer = EventsConsumer(
        kafka_consumer=app.state.kafka_consumer,
        extracted_invoice_data_event_manager=extracted_invoice_data_manager,
        ai_extraction_failure_manager=ai_extraction_failure_manager)
    
    asyncio.create_task(events_consumer.run_consumer())
    
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