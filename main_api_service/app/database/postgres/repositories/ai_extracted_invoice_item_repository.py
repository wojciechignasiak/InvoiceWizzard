from app.models.ai_extracted_invoice_item_model import CreateAIExtractedInvoiceItemModel, UpdateAIExtractedInvoiceItemModel
from app.schema.schema import AIExtractedInvoiceItem
from typing import List
from app.database.postgres.repositories.ai_extracted_invoice_item_repository_abc import AIExtractedInvoiceItemPostgresRepositoryABC
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

class AIExtractedInvoiceItemPostgresRepository(BasePostgresRepository, AIExtractedInvoiceItemPostgresRepositoryABC):
    
    async def create_extracted_invoice_item(self,
                                            user_id: str,
                                            extracted_invoice_id: str,
                                            ai_extracted_invoice_item: CreateAIExtractedInvoiceItemModel) -> AIExtractedInvoiceItem:
        try:
            stmt = (
                insert(AIExtractedInvoiceItem).
                values(
                    id=ai_extracted_invoice_item.id,
                    user_id=user_id,
                    extracted_invoice_id=extracted_invoice_id,
                    item_description=ai_extracted_invoice_item.item_description,
                    number_of_items=ai_extracted_invoice_item.number_of_items,
                    net_value=ai_extracted_invoice_item.net_value,
                    gross_value=ai_extracted_invoice_item.gross_value
                ). 
                returning(AIExtractedInvoiceItem)
            )
            created_ai_extracted_invoice_item = await self.session.scalar(stmt)
            return created_ai_extracted_invoice_item
        except IntegrityError as e:
            logger.error(f"AIExtractedInvoiceItemPostgresRepository.create_extracted_invoice_item() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new extracted invoice item in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoiceItemPostgresRepository.create_extracted_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_all_extracted_invoice_item_data_by_extracted_invoice_id(self, 
                                                                        extracted_invoice_id: str,
                                                                        user_id: str) -> List[AIExtractedInvoiceItem]:
        try:
            stmt = (
                select(AIExtractedInvoiceItem).
                where(
                    AIExtractedInvoiceItem.user_id == user_id,
                    AIExtractedInvoiceItem.extracted_invoice_id == extracted_invoice_id
                )
            )
            ai_extracted_invoice_items = await self.session.scalar(stmt)
            if ai_extracted_invoice_items == None:
                raise PostgreSQLNotFoundError("Extracted invoice items with provided invoice id not found in database.")
            return ai_extracted_invoice_items
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoiceItemPostgresRepository.get_all_extracted_invoice_item_data_by_extracted_invoice_id() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def update_extracted_invoice_item(self, user_id: str, update_ai_extracted_invoice_item: UpdateAIExtractedInvoiceItemModel) -> None:
        try:
            stmt = (
                update(AIExtractedInvoiceItem).
                where(
                    AIExtractedInvoiceItem.id == update_ai_extracted_invoice_item.id,
                    AIExtractedInvoiceItem.user_id == user_id,
                    AIExtractedInvoiceItem.extracted_invoice_id == update_ai_extracted_invoice_item.extracted_invoice_id
                ).
                values(
                    item_description=update_ai_extracted_invoice_item.item_description,
                    number_of_items=update_ai_extracted_invoice_item.number_of_items,
                    net_value=update_ai_extracted_invoice_item.net_value,
                    gross_value=update_ai_extracted_invoice_item.gross_value
                ).
                returning(AIExtractedInvoiceItem)
            )
            ai_extracted_invoice_item = await self.session.scalar(stmt)
            if ai_extracted_invoice_item == None:
                raise PostgreSQLNotFoundError("Extracted invoice item with provided id not found in database.")
            return ai_extracted_invoice_item
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoicePostgresRepository.update_extracted_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def delete_extracted_invoice_item(self, extracted_invoice_item_id: str, user_id: str) -> bool:
        try:
            stmt = (
                delete(AIExtractedInvoiceItem).
                where(
                    AIExtractedInvoiceItem.id == extracted_invoice_item_id,
                    AIExtractedInvoiceItem.user_id == user_id
                )
            )
            deleted_extracted_invoice_item = await self.session.execute(stmt)
            rows_after_delete = deleted_extracted_invoice_item.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoiceItemPostgresRepository.delete_extracted_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def delete_extracted_invoice_items(self, extracted_invoice_id: str, user_id: str) -> bool:
        try:
            stmt = (
                delete(AIExtractedInvoiceItem).
                where(
                    AIExtractedInvoiceItem.id == extracted_invoice_id,
                    AIExtractedInvoiceItem.user_id == user_id
                )
            )
            deleted_extracted_invoice_item = await self.session.execute(stmt)
            rows_after_delete = deleted_extracted_invoice_item.rowcount

            if rows_after_delete >= 0:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"AIExtractedInvoiceItemPostgresRepository.delete_extracted_invoice_items() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")