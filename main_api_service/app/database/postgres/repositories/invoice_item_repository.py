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

class InvoiceItemPostgresRepository(BasePostgresRepository, InvoiceItemPostgresRepositoryABC):

    async def create_invoice_item(self, user_id: str, invoice_id: str, new_invoice_item: CreateInvoiceItemModel) -> InvoiceItem:
        try:
            stmt = (
                insert(InvoiceItem).
                values(
                    id=new_invoice_item.id,
                    user_id=user_id,
                    invoice_id=invoice_id,
                    item_description=new_invoice_item.item_description,
                    number_of_items=new_invoice_item.number_of_items,
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

    async def get_invoice_item(self, user_id: str, invoice_item_id: str) -> InvoiceItem:
        try:
            stmt = (
                select(InvoiceItem).
                where(
                    InvoiceItem.id == invoice_item_id,
                    InvoiceItem.user_id == user_id
                )
            )
            invoice_item = await self.session.scalar(stmt)
            if invoice_item == None:
                raise PostgreSQLNotFoundError("Invoice item with provided id not found in database.")
            return invoice_item
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.get_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_invoice_items_by_invoice_id(self, user_id: str, invoice_id: str, in_trash: bool) -> list:
        try:
            stmt = (
                select(InvoiceItem).
                where(
                    InvoiceItem.invoice_id == invoice_id,
                    InvoiceItem.user_id == user_id,
                    InvoiceItem.in_trash == in_trash
                )
            )
            invoice_items = await self.session.scalars(stmt)
            if not invoice_items:
                raise PostgreSQLNotFoundError("Invoice items with provided invoice id not found in database.")
            return invoice_items.all()
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.get_invoice_items_by_invoice_id() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def update_invoice_item(self, user_id: str, update_invoice_item: UpdateInvoiceItemModel) -> None:
        try:
            stmt = (
                update(InvoiceItem).
                where(
                    InvoiceItem.id == update_invoice_item.id,
                    InvoiceItem.user_id == user_id
                    ).
                values(
                    invoice_id=update_invoice_item.invoice_id,
                    item_description=update_invoice_item.item_description,
                    number_of_items=update_invoice_item.number_of_items,
                    net_value=update_invoice_item.net_value,
                    gross_value=update_invoice_item.gross_value,
                ).
                returning(InvoiceItem)
            )
            updated_invoice_item = await self.session.scalar(stmt)
            if updated_invoice_item == None:
                raise PostgreSQLNotFoundError("Invoice item with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoiceItemPostgresRepository.update_invoice_item() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def update_invoice_item_in_trash_status(self, user_id: str, invoice_item_id: str, in_trash: bool) -> None:
        try:
            stmt = (
                update(InvoiceItem).
                where(
                    InvoiceItem.id == invoice_item_id,
                    InvoiceItem.user_id == user_id
                    ).
                values(
                in_trash=in_trash
                )
                .returning(InvoiceItem)
            )
            updated_invoice = await self.session.scalar(stmt)
            if updated_invoice == None:
                raise PostgreSQLNotFoundError("Invoice item with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.update_invoice_item_in_trash_status() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def update_all_invoice_items_in_trash_status_by_invoice_id(self, user_id: str, invoice_id: str, in_trash: bool) -> None:
        try:
            stmt = (
                update(InvoiceItem).
                where(
                    InvoiceItem.invoice_id == invoice_id,
                    InvoiceItem.user_id == user_id
                    ).
                values(
                in_trash=in_trash
                )
            )
            await self.session.execute(stmt)
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.update_invoice_item_in_trash_status() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def remove_invoice_item(self, user_id: str, invoice_item_id: str) -> bool:
        try:
            stmt = (
                delete(InvoiceItem).
                where(
                    InvoiceItem.id == invoice_item_id,
                    InvoiceItem.user_id == user_id
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