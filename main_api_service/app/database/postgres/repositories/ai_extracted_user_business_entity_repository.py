from app.models.ai_extracted_user_business_entity_model import CreateAIExtractedUserBusinessModel, UpdateAIExtractedUserBusinessModel
from app.schema.schema import AIExtractedUserBusinessEntity
from app.database.postgres.repositories.ai_extracted_user_business_entity_repository_abc import AIExtractedUserBusinessEntityPostgresRepositoryABC
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


class AIExtractedUserBusinessEntityPostgresRepository(BasePostgresRepository, AIExtractedUserBusinessEntityPostgresRepositoryABC):

    async def create_extracted_user_business_entity(self, 
                                                    user_id: str, 
                                                    extracted_invoice_id: str, 
                                                    ai_extracted_user_business_entity: CreateAIExtractedUserBusinessModel) -> AIExtractedUserBusinessEntity:
        try:
            stmt = (
                insert(AIExtractedUserBusinessEntity).
                values(
                    id=ai_extracted_user_business_entity.id,
                    user_id=user_id,
                    extracted_invoice_id=extracted_invoice_id,
                    company_name=ai_extracted_user_business_entity.company_name,
                    city=ai_extracted_user_business_entity.city,
                    postal_code=ai_extracted_user_business_entity.postal_code,
                    nip=ai_extracted_user_business_entity.nip
                ). 
                returning(AIExtractedUserBusinessEntity)
            )
            created_ai_extracted_user_business_entity = await self.session.scalar(stmt)
            return created_ai_extracted_user_business_entity
        except IntegrityError as e:
            logger.error(f"AIExtractedUserBusinessEntityPostgresRepository.create_extracted_user_external_business_entity() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new extracted user business entity in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedUserBusinessEntityPostgresRepository.create_extracted_user_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_extracted_user_business_entity(self, 
                                                        extracted_invoice_id: str, 
                                                        user_id: str) -> AIExtractedUserBusinessEntity:
        try:
            stmt = (
                select(AIExtractedUserBusinessEntity).
                where(
                    AIExtractedUserBusinessEntity.extracted_invoice_id == extracted_invoice_id,
                    AIExtractedUserBusinessEntity.user_id == user_id
                )
            )
            ai_extracted_user_business_entity = await self.session.scalar(stmt)
            if ai_extracted_user_business_entity == None:
                raise PostgreSQLNotFoundError("Extracted user business entity with provided invoice id not found in database.")
            return ai_extracted_user_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedUserBusinessEntityPostgresRepository.get_extracted_user_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def update_extracted_user_business_entity(self, 
                                                            update_ai_extracted_user_business_entity: UpdateAIExtractedUserBusinessModel, 
                                                            user_id: str) -> None:
        try:
            stmt = (
                update(AIExtractedUserBusinessEntity).
                where(
                    AIExtractedUserBusinessEntity.extracted_invoice_id == update_ai_extracted_user_business_entity.extracted_invoice_id,
                    AIExtractedUserBusinessEntity.user_id == user_id
                ).
                values(
                    company_name=update_ai_extracted_user_business_entity.company_name,
                    city=update_ai_extracted_user_business_entity.city,
                    postal_code=update_ai_extracted_user_business_entity.postal_code,
                    nip=update_ai_extracted_user_business_entity.nip
                ).
                returning(AIExtractedUserBusinessEntity)
            )

            ai_extracted_external_business_entity = await self.session.scalar(stmt)
            if ai_extracted_external_business_entity == None:
                raise PostgreSQLNotFoundError("Extracted user business entity with provided id not found in database.")
            return ai_extracted_external_business_entity
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedUserBusinessEntityPostgresRepository.update_extracted_user_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def delete_extracted_user_business_entity(self, 
                                                            extracted_invoice_id: str, 
                                                            user_id: str) -> bool:
        try:
            stmt = (
                delete(AIExtractedUserBusinessEntity).
                where(
                    AIExtractedUserBusinessEntity.extracted_invoice_id == extracted_invoice_id,
                    AIExtractedUserBusinessEntity.user_id == user_id
                )
            )
            deleted_extracted_user_business_entity = await self.session.execute(stmt)
            rows_after_delete = deleted_extracted_user_business_entity.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedUserBusinessEntityPostgresRepository.delete_extracted_user_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")