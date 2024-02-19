from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.ai_extraction_failure_repository_abc import AIExtractionFailurePostgresRepositoryABC
from app.models.ai_extraction_failure_model import CreateAIExtractionFailureModel
from app.schema.schema import AIExtractionFailure
from sqlalchemy import insert, select, delete
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

class AIExtractionFailurePostgresRepository(BasePostgresRepository, AIExtractionFailurePostgresRepositoryABC):
    
    async def create_ai_extraction_failure(self, 
                                            ai_extraction_failure_model: CreateAIExtractionFailureModel) -> AIExtractionFailure:
        try:
            stmt = (
                insert(AIExtractionFailure).
                values(
                    id=ai_extraction_failure_model.id,
                    user_id=ai_extraction_failure_model.user_id,
                    date=ai_extraction_failure_model.date,
                    invoice_pdf=ai_extraction_failure_model.invoice_pdf,
                    
                ). 
                returning(AIExtractionFailure)
            )
            created_ai_extraction_failure = await self.session.scalar(stmt)
            return created_ai_extraction_failure
        except IntegrityError as e:
            logger.error(f"AIExtractionFailurePostgresRepository.create_ai_extraction_failure() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new ai extraction failure in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractionFailurePostgresRepository.create_ai_extraction_failure() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_ai_extraction_failure(self, 
                                        ai_extraction_failure_id: str, 
                                        user_id: str) -> AIExtractionFailure:
        try:
            stmt = (
                select(AIExtractionFailure).
                where(
                    AIExtractionFailure.id == ai_extraction_failure_id,
                    AIExtractionFailure.user_id == user_id
                )
            )
            ai_extraction_failure = await self.session.scalar(stmt)
            if ai_extraction_failure is None:
                raise PostgreSQLNotFoundError("AI Extraction Failure with provided id not found in database.")
            return ai_extraction_failure
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractionFailurePostgresRepository.get_ai_extraction_failure() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_all_ai_extraction_failure(self,
                                            user_id: str,
                                            page: int = 1, 
                                            items_per_page: int = 10) -> list[AIExtractionFailure]:
        try:
            stmt = (
                select(AIExtractionFailure).
                where(
                    AIExtractionFailure.user_id == user_id
                ).
                limit(items_per_page).
                offset((page - 1) * items_per_page)
            )

            invoices = await self.session.scalars(stmt)
            if not invoices:
                raise PostgreSQLNotFoundError("No AI Extraction Failures found in database.")
            return invoices
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractionFailurePostgresRepository.get_all_ai_extraction_failure() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def delete_ai_extraction_failure(self, 
                                            extracted_invoice_id: str, 
                                            user_id: str) -> bool:
        try:
            stmt = (
                delete(AIExtractionFailure).
                where(
                    AIExtractionFailure.id == extracted_invoice_id,
                    AIExtractionFailure.user_id == user_id
                    )
            )
            deleted_ai_extraction_failure = await self.session.execute(stmt)
            rows_after_delete = deleted_ai_extraction_failure.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractionFailurePostgresRepository.delete_ai_extraction_failure() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")