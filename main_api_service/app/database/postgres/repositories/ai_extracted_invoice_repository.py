from abc import ABC, abstractmethod
from app.models.ai_extracted_invoice_model import CreateAIExtractedInvoiceModel, UpdateAIExtractedInvoiceModel
from app.schema.schema import AIExtractedInvoice
from typing import List
from app.database.postgres.repositories.ai_extracted_invoice_repository_abc import AIExtractedInvoicePostgresRepositoryABC
from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from sqlalchemy import insert, select, update, delete, func
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

class AIExtractedInvoicePostgresRepository(BasePostgresRepository, AIExtractedInvoicePostgresRepositoryABC):

    async def create_extracted_invoice(self, user_id: str, 
                                        ai_extracted_invoice: CreateAIExtractedInvoiceModel) -> AIExtractedInvoice:
        try:
            stmt = (
                insert(AIExtractedInvoice).
                values(
                    id=ai_extracted_invoice.id,
                    user_id=user_id,
                    invoice_pdf=ai_extracted_invoice.invoice_pdf,
                    invoice_number=ai_extracted_invoice.invoice_number,
                    issue_date=ai_extracted_invoice.issue_date,
                    sale_date=ai_extracted_invoice.sale_date,
                    payment_method=ai_extracted_invoice.payment_method,
                    payment_deadline=ai_extracted_invoice.payment_deadline,
                    notes=ai_extracted_invoice.notes,
                    added_date=ai_extracted_invoice.added_date,
                    is_issued=ai_extracted_invoice.is_issued
                ). 
                returning(AIExtractedInvoice)
            )
            created_ai_extracted_invoice = await self.session.scalar(stmt)
            return created_ai_extracted_invoice
        except IntegrityError as e:
            logger.error(f"AIExtractedInvoicePostgresRepository.create_extracted_invoice() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new invoice in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoicePostgresRepository.create_extracted_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_extracted_invoice(self,
                                    extracted_invoice_id: str, 
                                    user_id: str) -> AIExtractedInvoice:
        try:
            stmt = (
                select(AIExtractedInvoice).
                where(
                    AIExtractedInvoice.id == extracted_invoice_id,
                    AIExtractedInvoice.user_id == user_id
                )
            )
            ai_extracted_invoice = await self.session.scalar(stmt)
            if ai_extracted_invoice == None:
                raise PostgreSQLNotFoundError("Extracted invoice with provided id not found in database.")
            return ai_extracted_invoice
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoicePostgresRepository.get_extracted_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_all_extracted_invoices(self, 
                                        user_id: str,
                                        page: int = 1, 
                                        items_per_page: int = 10) -> List[AIExtractedInvoice]:
        try:
            stmt = (
                select(AIExtractedInvoice).
                where(
                    AIExtractedInvoice.user_id == user_id
                ).
                limit(items_per_page).
                offset((page - 1) * items_per_page)
            )
            ai_extracted_invoice = await self.session.scalar(stmt)
            if ai_extracted_invoice == None:
                raise PostgreSQLNotFoundError("Extracted invoice with provided id not found in database.")
            return ai_extracted_invoice
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoicePostgresRepository.get_all_extracted_invoices() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def update_extracted_invoice(self, 
                                        user_id: str,
                                        ai_update_extracted_invoice: UpdateAIExtractedInvoiceModel) -> None:
        try:
            stmt = (
                update(AIExtractedInvoice).
                where(
                    AIExtractedInvoice.id == ai_update_extracted_invoice.id,
                    AIExtractedInvoice.user_id == user_id
                ).
                values(
                    invoice_number=ai_update_extracted_invoice.invoice_number,
                    issue_date=ai_update_extracted_invoice.issue_date,
                    sale_date=ai_update_extracted_invoice.sale_date,
                    payment_method=ai_update_extracted_invoice.payment_method,
                    payment_deadline=ai_update_extracted_invoice.payment_deadline,
                    notes=ai_update_extracted_invoice.notes,
                    is_issued=ai_update_extracted_invoice.is_issued
                ).
                returning(AIExtractedInvoice)
            )
            ai_extracted_invoice = await self.session.scalar(stmt)
            if ai_extracted_invoice == None:
                raise PostgreSQLNotFoundError("Extracted invoice with provided id not found in database.")
            return ai_extracted_invoice
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoicePostgresRepository.update_extracted_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def delete_extracted_invoice(self, extracted_invoice_id: str, user_id: str) -> bool:
        try:
            stmt = (
                delete(AIExtractedInvoice).
                where(
                    AIExtractedInvoice.id == extracted_invoice_id,
                    AIExtractedInvoice.user_id == user_id
                )
            )
            deleted_extracted_invoice = await self.session.execute(stmt)
            rows_after_delete = deleted_extracted_invoice.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoicePostgresRepository.delete_extracted_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")