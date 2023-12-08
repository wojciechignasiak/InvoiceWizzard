from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.invoice_postgres_repository_abc import InvoicePostgresRepositoryABC
from app.models.invoice_model import CreateInvoiceManuallyModel
from app.schema.schema import Invoice
from sqlalchemy import insert, select
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
from uuid import uuid4, UUID
from datetime import datetime, date


class InvoicePostgresRepository(BasePostgresRepository, InvoicePostgresRepositoryABC):
    
    async def create_invoice_manually(self, user_id: str, invoice_pdf_location: str, new_invoice: CreateInvoiceManuallyModel) -> Invoice:
        try:
            stmt = (
                insert(Invoice).
                values(
                    id=uuid4(),
                    user_id=UUID(user_id),
                    user_business_entity_id=UUID(new_invoice.user_business_entity_id),
                    external_business_entity_id=UUID(new_invoice.external_business_entity_id),
                    invoice_pdf=invoice_pdf_location,
                    invoice_number=new_invoice.invoice_number,
                    issue_date=datetime.strptime(new_invoice.issue_date, '%Y-%m-%d').date(),
                    sale_date=datetime.strptime(new_invoice.sale_date, '%Y-%m-%d').date(),
                    payment_method=new_invoice.payment_method,
                    payment_deadline=datetime.strptime(new_invoice.payment_deadline, '%Y-%m-%d').date(),
                    added_date=date.today(),
                    is_settled=new_invoice.is_settled,
                    is_accepted=new_invoice.is_accepted,
                    is_issued=new_invoice.is_issued,
                ). 
                returning(Invoice)
            )
            created_invoice = await self.session.scalar(stmt)
            return created_invoice
        except IntegrityError as e:
            logger.error(f"InvoicePostgresRepository.create_invoice_manually() Error: {e}")
            raise PostgreSQLIntegrityError("Cannot create new invoice in database. Integrity error occured.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.create_invoice_manually() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
    
    async def get_invoice(self, user_id: str, invoice_id: str) -> Invoice:
        try:
            stmt = (
                select(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                )
            )
            invoice = await self.session.scalar(stmt)
            if invoice == None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
            return invoice
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.get_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")