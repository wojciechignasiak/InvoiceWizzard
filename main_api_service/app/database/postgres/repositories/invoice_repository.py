from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.invoice_repository_abc import InvoicePostgresRepositoryABC
from app.models.invoice_model import CreateInvoiceModel, UpdateInvoiceModel
from app.schema.schema import Invoice
from sqlalchemy import insert, select, or_, and_, update, delete
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
from typing import Optional
from app.logging import logger
from uuid import UUID


class InvoicePostgresRepository(BasePostgresRepository, InvoicePostgresRepositoryABC):
    
    async def create_invoice(self, user_id: str, new_invoice: CreateInvoiceModel) -> Invoice:
        try:
            stmt = (
                insert(Invoice).
                values(
                    id=new_invoice.id,
                    user_id=UUID(user_id),
                    user_business_entity_id=new_invoice.user_business_entity_id,
                    external_business_entity_id=new_invoice.external_business_entity_id,
                    invoice_pdf=None,
                    invoice_number=new_invoice.invoice_number,
                    issue_date=new_invoice.issue_date,
                    sale_date=new_invoice.sale_date,
                    payment_method=new_invoice.payment_method,
                    payment_deadline=new_invoice.payment_deadline,
                    notes=new_invoice.notes,
                    added_date=new_invoice.added_date,
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
        
    async def get_all_invoices(
                                self, 
                                user_id: str, 
                                page: int = 1, 
                                items_per_page: int = 10,
                                user_business_entity_id: Optional[str] = None,
                                user_business_entity_name: Optional[str] = None,
                                external_business_entity_id: Optional[str] = None,
                                external_business_entity_name: Optional[str] = None,
                                invoice_number: Optional[str] = None,
                                start_issue_date: Optional[str] = None,
                                end_issue_date: Optional[str] = None,
                                start_sale_date: Optional[str] = None,
                                end_sale_date: Optional[str] = None,
                                payment_method: Optional[str] = None,
                                start_payment_deadline: Optional[str] = None,
                                end_payment_deadline: Optional[str] = None,
                                start_added_date: Optional[str] = None,
                                end_added_date: Optional[str] = None,
                                is_settled: Optional[bool] = None,
                                is_accepted: Optional[bool] = None,
                                is_issued: Optional[bool] = None) -> list:
        try:
            stmt = (
                select(Invoice).
                where(
                    and_(
                        Invoice.user_id == user_id,
                        Invoice.user_business_entity_id == user_business_entity_id if user_business_entity_id else True,
                        Invoice.user_business_entity.company_name.ilike(f"%{user_business_entity_name}%") if user_business_entity_name else True,
                        Invoice.external_business_entity_id == external_business_entity_id if external_business_entity_id else True,
                        Invoice.external_business_entity.company_name.ilike(f"%{external_business_entity_name}%") if external_business_entity_name else True,
                        Invoice.invoice_number.ilike(f"%{invoice_number}%") if invoice_number else True,
                        or_(
                            and_(
                                Invoice.issue_date >= start_issue_date,
                                or_(end_issue_date is None, Invoice.issue_date <= end_issue_date)
                            ) if start_issue_date else True,
                        ),
                        or_(
                            and_(
                                Invoice.sale_date >= start_sale_date,
                                or_(end_sale_date is None, Invoice.sale_date <= end_sale_date)
                            ) if start_sale_date else True,
                        ),
                        Invoice.payment_method.ilike(f"%{payment_method}%") if payment_method else True,
                        or_(
                            and_(
                                Invoice.payment_deadline >= start_payment_deadline,
                                or_(end_payment_deadline is None, Invoice.payment_deadline <= end_payment_deadline)
                            ) if start_payment_deadline else True,
                        ),
                        or_(
                            and_(
                                Invoice.added_date >= start_added_date,
                                or_(end_added_date is None, Invoice.added_date <= end_added_date)
                            ) if start_added_date else True,
                        ),
                        Invoice.is_settled == is_settled if is_settled is not None else True,
                        Invoice.is_accepted == is_accepted if is_accepted is not None else True,
                        Invoice.is_issued == is_issued if is_issued is not None else True
                    )
                ).
                limit(items_per_page).
                offset((page - 1) * items_per_page)
            )

            invoices = await self.session.scalars(stmt)
            if not invoices:
                raise PostgreSQLNotFoundError("No invoices found in database.")
            return invoices
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.get_all_invoices() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def update_invoice(self, user_id: str, update_invoice: UpdateInvoiceModel) -> None:
        try:
            stmt = (
                update(Invoice).
                where(
                    Invoice.id == update_invoice.id,
                    Invoice.user_id == user_id
                    ).
                values(
                    user_business_entity_id=update_invoice.user_business_entity_id,
                    external_business_entity_id=update_invoice.external_business_entity_id,
                    invoice_number=update_invoice.invoice_number,
                    issue_date=update_invoice.issue_date,
                    sale_date=update_invoice.sale_date,
                    payment_method=update_invoice.payment_method,
                    payment_deadline=update_invoice.payment_deadline,
                    notes=update_invoice.notes,
                    is_settled=update_invoice.is_settled,
                    is_accepted=update_invoice.is_accepted,
                    is_issued=update_invoice.is_issued
                ).
                returning(Invoice)
            )
            updated_invoice = await self.session.scalar(stmt)
            if updated_invoice == None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.update_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def remove_invoice(self, user_id: str, invoice_id: str) -> bool:
        try:
            stmt = (
                delete(Invoice).
                where(
                    Invoice.id == UUID(invoice_id),
                    Invoice.user_id == UUID(user_id)
                    )
            )
            deleted_invoice = await self.session.execute(stmt)
            rows_after_delete = deleted_invoice.rowcount

            if rows_after_delete == 1:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.remove_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def is_invoice_unique(self, user_id: str, new_invoice: CreateInvoiceModel) -> bool:
        try:
            stmt = (
                select(Invoice).
                where(
                    (Invoice.user_id == user_id) & 
                    (Invoice.user_business_entity_id == new_invoice.user_business_entity_id) & 
                    (Invoice.external_business_entity_id == new_invoice.external_business_entity_id) &
                    (Invoice.invoice_number == new_invoice.invoice_number) &
                    (Invoice.is_issued == new_invoice.is_issued) 
                    )
                )
            invoice = await self.session.scalar(stmt)
            if invoice == None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.is_invoice_unique() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
    
    async def is_invoice_unique_beside_one_to_update(self, user_id: str, update_invoice: UpdateInvoiceModel) -> bool:
        try:
            stmt = (
                select(Invoice).
                where(
                    (Invoice.id != update_invoice.id) &
                    (Invoice.user_id == user_id) & 
                    (Invoice.user_business_entity_id == update_invoice.user_business_entity_id) & 
                    (Invoice.external_business_entity_id == update_invoice.external_business_entity_id) &
                    (Invoice.invoice_number == update_invoice.invoice_number) &
                    (Invoice.is_issued == update_invoice.is_issued) 
                    )
                )
            invoice = await self.session.scalar(stmt)
            if invoice == None:
                return True
            else:
                return False
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.is_invoice_unique_beside_one_to_update() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def update_invoice_file(self, user_id: str, invoice_id: str, invoice_pdf_location: str) -> None:
        try:
            stmt = (
                update(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                    ).
                values(
                    invoice_pdf=invoice_pdf_location
                ).
                returning(Invoice)
            )
            updated_invoice = await self.session.scalar(stmt)
            if updated_invoice == None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.update_invoice_file() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
    
    
    async def remove_invoice_file(self, user_id: str, invoice_id: str) -> None:
        try:
            stmt = (
                update(Invoice).
                where(
                    Invoice.id == UUID(invoice_id),
                    Invoice.user_id == UUID(user_id)
                    ).
                values(
                    invoice_pdf=None
                ).
                returning(Invoice)
            )
            removed_invoice_file = await self.session.scalar(stmt)
            if removed_invoice_file == None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.remove_invoice_file() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")