from app.models.ai_is_external_business_entity_recognized_model import CreateAIIsExternalBusinessEntityRecognizedModel, UpdateAIIsExternalBusinessEntityRecognizedModel
from app.schema.schema import AIIsExternalBusinessEntityRecognized
from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.ai_is_external_business_recognized_repository_abc import AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC
from sqlalchemy import insert, select, update, delete
from app.database.postgres.exceptions.custom_postgres_exceptions import (
    PostgreSQLDatabaseError,
    PostgreSQLIntegrityError,
    PostgreSQLNotFoundError,
)
from sqlalchemy.exc import (
    IntegrityError, 
    DataError, 
    StatementError,
    DatabaseError,
    InterfaceError,
    OperationalError,
    ProgrammingError
    )
from app.logging import logger

class AIIsExternalBusinessEntityRecognizedPostgresRepository(BasePostgresRepository, AIIsExternalBusinessEntityRecognizedPostgresRepositoryABC):
    
    async def create_is_external_business_entity_recognized(self, 
                                                            user_id: str, 
                                                            extracted_invoice_id: str, 
                                                            ai_is_external_business_recognized: CreateAIIsExternalBusinessEntityRecognizedModel) -> AIIsExternalBusinessEntityRecognized:
        try:
            stmt = (
                insert(AIIsExternalBusinessEntityRecognized).
                values(
                    id=ai_is_external_business_recognized.id,
                    user_id=user_id,
                    extracted_invoice_id=extracted_invoice_id,
                    is_recognized=ai_is_external_business_recognized.is_recognized,
                    external_business_entity_id=ai_is_external_business_recognized.external_business_entity_id,
                ). 
                returning(AIIsExternalBusinessEntityRecognized)
            )
            created_ai_is_external_business_entity_recognized = await self.session.scalar(stmt)
            return created_ai_is_external_business_entity_recognized
        except IntegrityError as e:
            logger.error(f"AIIsExternalBusinessRecognizedPostgresRepository.create_is_external_business_recognized() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new is external business entity recognise in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIIsExternalBusinessRecognizedPostgresRepository.create_is_external_business_recognized() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_is_external_business_entity_recognized(self, 
                                                        extracted_invoice_id: str, 
                                                        user_id: str) -> AIIsExternalBusinessEntityRecognized:
        try:
            stmt = (
                select(AIIsExternalBusinessEntityRecognized).
                where(
                    AIIsExternalBusinessEntityRecognized.extracted_invoice_id == extracted_invoice_id,
                    AIIsExternalBusinessEntityRecognized.user_id == user_id
                )
            )
            ai_is_external_business_entity_recognized = await self.session.scalar(stmt)
            if ai_is_external_business_entity_recognized is None:
                raise PostgreSQLNotFoundError("Is external business entity recognized with provided invoice id not found in database.")
            return ai_is_external_business_entity_recognized
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIIsExternalBusinessRecognizedPostgresRepository.get_is_external_business_recognized() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def update_is_external_business_entity_recognized(self, 
                                                            user_id: str,
                                                            update_is_external_business_entity_recognized: UpdateAIIsExternalBusinessEntityRecognizedModel) -> None:
        try:
            stmt = (
                update(AIIsExternalBusinessEntityRecognized).
                where(
                    AIIsExternalBusinessEntityRecognized.extracted_invoice_id == update_is_external_business_entity_recognized.extracted_invoice_id,
                    AIIsExternalBusinessEntityRecognized.user_id == user_id
                ).
                values(
                    is_recognized=update_is_external_business_entity_recognized.is_recognized,
                    external_business_entity_id=update_is_external_business_entity_recognized.external_business_entity_id
                ).
                returning(AIIsExternalBusinessEntityRecognized)
            )

            ai_is_external_business_entity = await self.session.scalar(stmt)
            if ai_is_external_business_entity is None:
                raise PostgreSQLNotFoundError("Is external business entity recognized with provided invoice id not found in database.")
            return ai_is_external_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIIsExternalBusinessRecognizedPostgresRepository.update_is_external_business_recognized() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def delete_is_external_business_entity_recognized(self, 
                                                            extracted_invoice_id: str, 
                                                            user_id: str) -> bool:
        try:
            stmt = (
                delete(AIIsExternalBusinessEntityRecognized).
                where(
                    AIIsExternalBusinessEntityRecognized.extracted_invoice_id == extracted_invoice_id,
                    AIIsExternalBusinessEntityRecognized.user_id == user_id
                )
            )
            deleted_is_external_business_entity_recognized = await self.session.execute(stmt)
            rows_after_delete = deleted_is_external_business_entity_recognized.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIIsExternalBusinessRecognizedPostgresRepository.delete_is_external_business_recognized() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")