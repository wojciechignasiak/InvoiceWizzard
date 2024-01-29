from app.kafka.consumed_events_managers.extracted_invoice_data_event_manager_abc import ExtractedInvoiceDataMenagerABC
from app.models.ai_extracted_data_model import AIExtractedDataModel
from app.models.ai_extracted_invoice_model import AIExtractedInvoiceModel
from app.models.ai_extracted_invoice_model import CreateAIExtractedInvoiceModel
from app.models.ai_extracted_invoice_item_model import CreateAIExtractedInvoiceItemModel
from app.models.ai_extracted_user_business_entity_model import CreateAIExtractedUserBusinessModel
from app.models.ai_extracted_external_business_entity_model import CreateAIExtractedExternalBusinessModel
from app.models.ai_is_user_business_entity_recognized_model import CreateAIIsUserBusinessEntityRecognizedModel
from app.models.ai_is_external_business_entity_recognized_model import CreateAIIsExternalBusinessEntityRecognizedModel
from app.models.user_business_entity_model import UserBusinessEntityModel
from app.models.external_business_entity_model import ExternalBusinessEntityModel
from app.schema.schema import AIExtractedInvoice
from app.registries.repositories_registry_abc import RepositoriesRegistryABC
from app.types.postgres_repository_abstract_types import (
    AIExtractedInvoicePostgresRepositoryABC,
    AIExtractedUserBusinessEntityPostgresRepositoryABC,
    AIExtractedExternalBusinessEntityPostgresRepositoryABC,
    AIExtractedInvoiceItemPostgresRepositoryABC,
    AIIsUserBusinessRecognizedPostgresRepositoryABC,
    AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC,
    UserBusinessEntityPostgresRepositoryABC,
    ExternalBusinessEntityPostgresRepositoryABC
)
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession,
    AsyncEngine
)
from app.logging import logger
from typing import (
    Dict, 
    List
)

class ExtractedInvoiceDataMenager(ExtractedInvoiceDataMenagerABC):
    def __init__(self, repositories_registry: RepositoriesRegistryABC, postgres_url: str):
        
        self._repositories_registry: RepositoriesRegistryABC = repositories_registry
        self._engine: AsyncEngine = create_async_engine(
                                    postgres_url,
                                    echo=False,
                                    future=True
                                )

    async def create_invoice_data(self, invoice_data: Dict):
        try:
            async with self._engine.begin() as conn:
                
                session: AsyncSession = AsyncSession(conn)

                ai_extracted_data_model: AIExtractedDataModel = AIExtractedDataModel.model_validate(invoice_data)

                ai_extracted_invoice_model: AIExtractedInvoiceModel = await self._create_ai_extracted_invoice(
                    create_ai_extracted_invoice_model=ai_extracted_data_model.invoice,
                    user_id=ai_extracted_data_model.user_id,
                    session=session
                )

                await self._create_ai_extracted_invoice_items(
                    invoice_items=ai_extracted_data_model.invoice_items,
                    user_id=ai_extracted_data_model.user_id,
                    ai_extracted_invoice_id=ai_extracted_invoice_model.id,
                    session=session
                )

                await self._create_ai_extracted_user_business_entity(
                    create_ai_extracted_user_business_entity=ai_extracted_data_model.user_business_entity,
                    user_id=ai_extracted_data_model.user_id,
                    ai_extracted_invoice_id=ai_extracted_invoice_model.id,
                    session=session
                )

                await self._create_ai_extracted_external_business_entity(
                    create_ai_extracted_external_business_entity=ai_extracted_data_model.external_business_entity,
                    user_id=ai_extracted_data_model.user_id,
                    ai_extracted_invoice_id=ai_extracted_invoice_model.id,
                    session=session
                )

                if ai_extracted_data_model.user_business_entity.nip:
                    result_user_business_entity_recognition: List = await self.try_to_recognize_user_business_entity_by_nip(
                        user_id=ai_extracted_data_model.user_id,
                        nip=ai_extracted_data_model.user_business_entity.nip,
                        session=session
                    )
                    
                elif ai_extracted_data_model.user_business_entity.nip is None and ai_extracted_data_model.user_business_entity.company_name is not None:
                    result_user_business_entity_recognition: List = await self.try_to_recognize_user_business_entity_by_name(
                        user_id=ai_extracted_data_model.user_id,
                        company_name=ai_extracted_data_model.user_business_entity.company_name,
                        session=session
                    )

                if not result_user_business_entity_recognition:
                    create_ai_is_user_business_entity_recognized: CreateAIIsUserBusinessEntityRecognizedModel = CreateAIIsUserBusinessEntityRecognizedModel(
                        is_recognized=False,
                        user_business_entity_id=None
                    )
                else:
                    user_business_entity: UserBusinessEntityModel = await UserBusinessEntityModel.user_business_entity_schema_to_model(
                        result_user_business_entity_recognition[0]
                    )
                    create_ai_is_user_business_entity_recognized: CreateAIIsUserBusinessEntityRecognizedModel = CreateAIIsUserBusinessEntityRecognizedModel(
                        is_recognized=True,
                        user_business_entity_id=user_business_entity.id
                    )


                if ai_extracted_data_model.external_business_entity.nip:
                    result_external_business_entity_recognition: List = await self.try_to_recognize_external_business_entity_by_nip(
                        user_id=ai_extracted_data_model.user_id,
                        nip=ai_extracted_data_model.external_business_entity.nip,
                        session=session
                    )
                elif ai_extracted_data_model.external_business_entity.nip is None and ai_extracted_data_model.external_business_entity.name is not None:
                    result_external_business_entity_recognition: List = await self.try_to_recognize_external_business_entity_by_name(
                        user_id=ai_extracted_data_model.user_id,
                        name=ai_extracted_data_model.external_business_entity.name,
                        session=session
                    )
                    

                if not result_external_business_entity_recognition:
                    create_ai_is_external_business_entity_recognized: CreateAIIsExternalBusinessEntityRecognizedModel = CreateAIIsExternalBusinessEntityRecognizedModel(
                        is_recognized=False,
                        external_business_entity_id=None
                    )
                else:
                    external_business_entity: ExternalBusinessEntityModel = await ExternalBusinessEntityModel.external_business_entity_schema_to_model(
                        result_external_business_entity_recognition[0]
                    )
                    create_ai_is_external_business_entity_recognized: CreateAIIsExternalBusinessEntityRecognizedModel = CreateAIIsExternalBusinessEntityRecognizedModel(
                        is_recognized=True,
                        external_business_entity_id=external_business_entity.id
                    )

                await self._create_ai_is_extracted_user_business_entity_recognized(
                    create_ai_is_user_business_entity_recognized=create_ai_is_user_business_entity_recognized,
                    user_id=ai_extracted_data_model.user_id,
                    ai_extracted_invoice_id=ai_extracted_invoice_model.id,
                    session=session
                )
                
                await self._create_ai_is_extracted_external_business_entity_recognized(
                    create_ai_is_external_business_entity_recognized=create_ai_is_external_business_entity_recognized,
                    user_id=ai_extracted_data_model.user_id,
                    ai_extracted_invoice_id=ai_extracted_invoice_model.id,
                    session=session
                )

                await session.commit()

        except Exception as e:
            logger.error(f"ExtractedInvoiceDataMenager.create_invoice_data() Error: {e}")
            await session.rollback()
        finally:
            await session.close()

    async def _create_ai_extracted_invoice(self, create_ai_extracted_invoice_model: CreateAIExtractedInvoiceModel, user_id: str, session: AsyncSession) -> AIExtractedInvoiceModel:
        try:
            ai_extracted_invoice_repository: AIExtractedInvoicePostgresRepositoryABC = await self._repositories_registry.return_ai_extracted_invoice_postgres_repository(
                    session=session
                )
            
            ai_extracted_invoice: AIExtractedInvoice = await ai_extracted_invoice_repository.create_extracted_invoice(
                    user_id=user_id,
                    ai_extracted_invoice=create_ai_extracted_invoice_model)
                
            ai_extracted_invoice_model: AIExtractedInvoiceModel = await AIExtractedInvoiceModel.ai_extracted_invoice_schema_to_model(ai_extracted_invoice)
            return ai_extracted_invoice_model
        except Exception as e:
            logger.error(f"ExtractedInvoiceDataMenager._create_ai_extracted_invoice() Error: {e}")
        
    async def _create_ai_extracted_invoice_items(self, invoice_items: List[CreateAIExtractedInvoiceItemModel], user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        try:
            ai_extracted_invoice_item_repository: AIExtractedInvoiceItemPostgresRepositoryABC = await self._repositories_registry.return_ai_extracted_invoice_item_postgres_repository(
                    session=session
                )
            
            for invoice_item in invoice_items:
                    await ai_extracted_invoice_item_repository.create_extracted_invoice_item(
                        user_id=user_id,
                        extracted_invoice_id=ai_extracted_invoice_id,
                        ai_extracted_invoice_item=invoice_item
                    )
        except Exception as e:
            logger.error(f"ExtractedInvoiceDataMenager._create_ai_extracted_invoice_items() Error: {e}")
        
    async def _create_ai_extracted_user_business_entity(self, create_ai_extracted_user_business_entity: CreateAIExtractedUserBusinessModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        try:
            ai_extracted_user_business_entity_repository: AIExtractedUserBusinessEntityPostgresRepositoryABC = await self._repositories_registry.return_ai_extracted_user_business_entity_postgres_repository(
                    session=session
                )
            
            await ai_extracted_user_business_entity_repository.create_extracted_user_business_entity(
                    user_id=user_id,
                    extracted_invoice_id=ai_extracted_invoice_id,
                    ai_extracted_user_business_entity=create_ai_extracted_user_business_entity
                )
        except Exception as e:
            logger.error(f"ExtractedInvoiceDataMenager._create_ai_extracted_user_business_entity() Error: {e}")
        
    async def _create_ai_extracted_external_business_entity(self, create_ai_extracted_external_business_entity: CreateAIExtractedExternalBusinessModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        try:
            ai_extracted_external_business_entity_repository: AIExtractedExternalBusinessEntityPostgresRepositoryABC = await self._repositories_registry.return_ai_extracted_external_business_entity_postgres_repository(
                    session=session
                )
            await ai_extracted_external_business_entity_repository.create_extracted_external_business_entity(
                    user_id=user_id,
                    extracted_invoice_id=ai_extracted_invoice_id,
                    ai_extracted_external_business_entity=create_ai_extracted_external_business_entity
                )
        except Exception as e:
            logger.error(f"ExtractedInvoiceDataMenager._create_ai_extracted_external_business_entity() Error: {e}")
        
    async def _create_ai_is_extracted_user_business_entity_recognized(self, create_ai_is_user_business_entity_recognized: CreateAIIsUserBusinessEntityRecognizedModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        try:
            ai_is_user_business_entity_recognized_repository: AIIsUserBusinessRecognizedPostgresRepositoryABC = await self._repositories_registry.return_ai_is_user_business_recognized_postgres_repository(
                    session=session
                )
            
            await ai_is_user_business_entity_recognized_repository.create_is_user_business_recognized(
                    user_id=user_id,
                    extracted_invoice_id=ai_extracted_invoice_id,
                    ai_is_user_business_recognized=create_ai_is_user_business_entity_recognized
                )
        except Exception as e:
            logger.error(f"ExtractedInvoiceDataMenager._create_ai_is_extracted_user_business_entity_recognized() Error: {e}")
        
    async def _create_ai_is_extracted_external_business_entity_recognized(self, create_ai_is_external_business_entity_recognized: CreateAIIsExternalBusinessEntityRecognizedModel, user_id: str, ai_extracted_invoice_id: str, session: AsyncSession) -> None:
        try:
            ai_is_external_business_entity_recognized_repository: AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC = await self._repositories_registry.return_ai_is_external_business_recognized_postgres_repository(
                    session=session
                )
            
            await ai_is_external_business_entity_recognized_repository.create_is_external_business_entity_recognized(
                    user_id=user_id,
                    extracted_invoice_id=ai_extracted_invoice_id,
                    ai_is_external_business_recognized=create_ai_is_external_business_entity_recognized
                )
        except Exception as e:
            logger.error(f"ExtractedInvoiceDataMenager._create_ai_is_extracted_external_business_entity_recognized() Error: {e}")
        
    async def try_to_recognize_user_business_entity_by_name(self, user_id: str, name: str, session: AsyncSession) -> List:
        try:
            user_business_entity_repository: UserBusinessEntityPostgresRepositoryABC = await self._repositories_registry.return_user_business_entity_postgres_repository(
                session=session
            )
            
            result = await user_business_entity_repository.get_all_user_business_entities(
                items_per_page=1,
                user_id=user_id,
                name=name
            )
            return result
        except Exception:
            return []

    async def try_to_recognize_user_business_entity_by_nip(self, user_id: str, nip: str, session: AsyncSession) -> List:
        try:
            user_business_entity_repository: UserBusinessEntityPostgresRepositoryABC = await self._repositories_registry.return_user_business_entity_postgres_repository(
                session=session
                )
            
            result = await user_business_entity_repository.get_all_user_business_entities(
                items_per_page=1,
                user_id=user_id,
                nip=nip
            )
            return result
        except Exception:
            return []
    
    async def try_to_recognize_external_business_entity_by_name(self, user_id: str, name: str, session: AsyncSession) -> List:
        try:
            external_business_entity_repository: ExternalBusinessEntityPostgresRepositoryABC = await self._repositories_registry.return_external_business_entity_postgres_repository(
                session=session
            )
            
            result = await external_business_entity_repository.get_all_external_business_entities(
                items_per_page=1,
                user_id=user_id,
                name=name
            )
            return result
        except Exception as e:
            return []

    async def try_to_recognize_external_business_entity_by_nip(self, user_id: str, nip: str, session: AsyncSession) -> List:
        try:
            external_business_entity_repository: ExternalBusinessEntityPostgresRepositoryABC = await self._repositories_registry.return_external_business_entity_postgres_repository(
                session=session
            )
            
            result = await external_business_entity_repository.get_all_external_business_entities(
                items_per_page=1,
                user_id=user_id,
                nip=nip
            )
            return result
        except Exception as e:
            return []