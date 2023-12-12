from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.models.invoice_model import CreateInvoiceItemModel, UpdateInvoiceItemModel
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
from sqlalchemy import insert, select, or_, and_, update, delete
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
        pass

    async def get_invoice_items_from_invoice(self, invoice_id: str) -> list:
        pass

    async def update_invoice_item(self, update_invoice_item: UpdateInvoiceItemModel) -> InvoiceItem:
        pass

    async def remove_invoice_item(self, invoice_item_id: str) -> bool:
        pass