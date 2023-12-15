from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.models.invoice_item_model import UpdateInvoiceItemModel, CreateInvoiceItemModel
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
from app.schema.schema import InvoiceItem
from sqlalchemy import insert, select, update, delete
from app.logging import logger
from uuid import uuid4, UUID

class InvoiceItemPostgresRepository(BasePostgresRepository, InvoiceItemPostgresRepositoryABC):

    async def create_invoice_item(self, invoice_id: str, new_invoice_item: CreateInvoiceItemModel) -> InvoiceItem:
        try:
            stmt = (
                insert(InvoiceItem).
                values(
                    id=uuid4(),
                    invoice_id=UUID(invoice_id),
                    ordinal_number=new_invoice_item.ordinal_number,
                    invoice_description=new_invoice_item.invoice_description,
                    net_value=new_invoice_item.net_value,
                    gross_value=new_invoice_item.gross_value
                ). 
                returning(InvoiceItem)
            )
            created_invoice_item = await self.session.scalar(stmt)
            return created_invoice_item
        except IntegrityError as e:
            logger.error(f"InvoiceItemPostgresRepository.create_invoice_item() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new invoice item in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.create_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_invoice_item(self, invoice_item_id: str) -> InvoiceItem:
        try:
            stmt = (
                select(InvoiceItem).
                where(
                    InvoiceItem.id == invoice_item_id
                )
            )
            invoice_item = await self.session.scalar(stmt)
            if invoice_item == None:
                raise PostgreSQLNotFoundError("Invoice item with provided id not found in database.")
            return invoice_item
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.get_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_invoice_items_from_invoice(self, invoice_id: str) -> list:
        try:
            stmt = (
                select(InvoiceItem).
                where(
                    InvoiceItem.invoice_id == invoice_id
                )
            )
            invoice_items = await self.session.scalar(stmt)
            if not invoice_items:
                raise PostgreSQLNotFoundError("Invoice items with provided invoice id not found in database.")
            return invoice_items
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.get_invoice_items_from_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def update_invoice_item(self, update_invoice_item: UpdateInvoiceItemModel) -> InvoiceItem:
        try:
            stmt = (
                update(InvoiceItem).
                where(
                    InvoiceItem.id == update_invoice_item.id,
                    ).
                values(
                    invoice_id=update_invoice_item.invoice_id,
                    ordinal_number=update_invoice_item.ordinal_number,
                    invoice_description=update_invoice_item.invoice_description,
                    net_value=update_invoice_item.net_value,
                    gross_value=update_invoice_item.gross_value
                ).
                returning(InvoiceItem)
            )
            updated_invoice_item = await self.session.scalar(stmt)
            if updated_invoice_item == None:
                raise PostgreSQLNotFoundError("Invoice item with provided id not found in database.")
            return updated_invoice_item
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.update_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def remove_invoice_item(self, invoice_item_id: str) -> bool:
        try:
            stmt = (
                delete(InvoiceItem).
                where(
                    InvoiceItem.id == invoice_item_id
                )
            )
            deleted_invoice_item = await self.session.execute(stmt)
            rows_after_delete = deleted_invoice_item.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.remove_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")