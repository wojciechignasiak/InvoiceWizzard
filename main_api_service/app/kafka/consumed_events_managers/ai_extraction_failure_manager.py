from app.kafka.consumed_events_managers.ai_extraction_failure_manager_abc import AIExtractionFailureManagerABC
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from app.types.postgres_repository_abstract_types import (
    AIExtractionFailurePostgresRepositoryABC
)
from app.models.ai_extraction_failure_model import CreateAIExtractionFailureModel
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession,
    AsyncEngine
)
from app.logging import logger



class AIExtractionFailureManager(AIExtractionFailureManagerABC):

    def __init__(self, repositories_registry: RepositoriesRegistryABC, postgres_url: str):
        
        self._repositories_registry: RepositoriesRegistryABC = repositories_registry
        self._engine: AsyncEngine = create_async_engine(
                                    postgres_url,
                                    echo=False,
                                    future=True
                                )
    async def create_ai_extraction_failure(self, message: dict):
        try:
            async with self._engine.begin() as conn:
                
                session: AsyncSession = AsyncSession(conn)
                file_location_list: list = message["file_location"].split("/")


                create_ai_extraction_failure_model: CreateAIExtractionFailureModel = CreateAIExtractionFailureModel(
                    invoice_pdf=message["file_location"],
                    user_id=file_location_list[5]
                )
                ai_extraction_failure_postgres_repository: AIExtractionFailurePostgresRepositoryABC = await self._repositories_registry.return_ai_extraction_failure_postgres_repository(
                    session=session
                )
                
                await ai_extraction_failure_postgres_repository.create_ai_extraction_failure(
                    ai_extraction_failure_model=create_ai_extraction_failure_model
                )
        except Exception as e:
            logger.error(f"EAIExtractionFailureManager.create_ai_extraction_failure() Error: {e}")
            await session.rollback()
        finally:
            await session.close()