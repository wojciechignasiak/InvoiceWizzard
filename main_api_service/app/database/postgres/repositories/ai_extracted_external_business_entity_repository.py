from app.models.ai_extracted_external_business_entity_model import CreateAIExtractedExternalBusinessModel, UpdateAIExtractedExternalBusinessModel
from app.schema.schema import AIExtractedExternalBusinessEntity
from app.database.postgres.repositories.ai_extracted_external_business_entity_repository_abc import AIExtractedExternalBusinessEntityPostgresRepositoryABC
from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
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


class AIExtractedExternalBusinessEntityPostgresRepository(BasePostgresRepository, AIExtractedExternalBusinessEntityPostgresRepositoryABC):

    async def create_extracted_external_business_entity(self, 
                                                        user_id: str, 
                                                        extracted_invoice_id: str, 
                                                        ai_extracted_external_business_entity_data: CreateAIExtractedExternalBusinessModel) -> AIExtractedExternalBusinessEntity:
        try:
            stmt = (
                insert(AIExtractedExternalBusinessEntity).
                values(
                    id=ai_extracted_external_business_entity_data.id,
                    user_id=user_id,
                    extracted_invoice_id=extracted_invoice_id,
                    name=ai_extracted_external_business_entity_data.name,
                    city=ai_extracted_external_business_entity_data.city,
                    postal_code=ai_extracted_external_business_entity_data.postal_code,
                    nip=ai_extracted_external_business_entity_data.nip
                ). 
                returning(AIExtractedExternalBusinessEntity)
            )
            created_ai_extracted_external_business_entity = await self.session.scalar(stmt)
            return created_ai_extracted_external_business_entity
        except IntegrityError as e:
            logger.error(f"AIExtractedExternalBusinessEntityPostgresRepository.create_extracted_external_business_entity() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new extracted external business entity in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedExternalBusinessEntityPostgresRepository.create_extracted_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def get_extracted_external_business_entity(self, 
                                                    extracted_invoice_id: str, 
                                                    user_id: str) -> AIExtractedExternalBusinessEntity:
        try:
            stmt = (
                select(AIExtractedExternalBusinessEntity).
                where(
                    AIExtractedExternalBusinessEntity.extracted_invoice_id == extracted_invoice_id,
                    AIExtractedExternalBusinessEntity.user_id == user_id
                )
            )
            ai_extracted_external_business_entity = await self.session.scalar(stmt)
            if ai_extracted_external_business_entity == None:
                raise PostgreSQLNotFoundError("Extracted external business entity with provided invoice id not found in database.")
            return ai_extracted_external_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedExternalBusinessEntityPostgresRepository.get_extracted_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def update_extracted_external_business_entity(self,
                                                        user_id: str, 
                                                        update_ai_extracted_external_business_entity: UpdateAIExtractedExternalBusinessModel) -> None:
        try:
            stmt = (
                update(AIExtractedExternalBusinessEntity).
                where(
                    AIExtractedExternalBusinessEntity.extracted_invoice_id == update_ai_extracted_external_business_entity.extracted_invoice_id,
                    AIExtractedExternalBusinessEntity.user_id == user_id
                ).
                values(
                    name=update_ai_extracted_external_business_entity.name,
                    city=update_ai_extracted_external_business_entity.city,
                    postal_code=update_ai_extracted_external_business_entity.postal_code,
                    nip=update_ai_extracted_external_business_entity.nip
                ).
                returning(AIExtractedExternalBusinessEntity)
            )

            ai_extracted_external_business_entity = await self.session.scalar(stmt)
            if ai_extracted_external_business_entity == None:
                raise PostgreSQLNotFoundError("Extracted external business entity with provided id not found in database.")
            return ai_extracted_external_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedExternalBusinessEntityPostgresRepository.update_extracted_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")


    async def delete_extracted_external_business_entity(self, 
                                                        extracted_invoice_id: str, 
                                                        user_id: str) -> bool:
        try:
            stmt = (
                delete(AIExtractedExternalBusinessEntity).
                where(
                    AIExtractedExternalBusinessEntity.extracted_invoice_id == extracted_invoice_id,
                    AIExtractedExternalBusinessEntity.user_id == user_id
                )
            )
            deleted_extracted_external_business_entity = await self.session.execute(stmt)
            rows_after_delete = deleted_extracted_external_business_entity.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedExternalBusinessEntityPostgresRepository.delete_extracted_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")