from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.invoice_repository_abc import InvoicePostgresRepositoryABC
from app.models.invoice_model import CreateInvoiceModel, UpdateInvoiceModel
from app.schema.schema import Invoice, ExternalBusinessEntity, UserBusinessEntity
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
from typing import Optional
from app.logging import logger
from datetime import date


class InvoicePostgresRepository(BasePostgresRepository, InvoicePostgresRepositoryABC):
    
    async def create_invoice(self, user_id: str, new_invoice: CreateInvoiceModel) -> Invoice:
        try:
            stmt = (
                insert(Invoice).
                values(
                    id=new_invoice.id,
                    user_id=user_id,
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
            if invoice is None:
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
                                start_issue_date: Optional[date] = None,
                                end_issue_date: Optional[date] = None,
                                start_sale_date: Optional[date] = None,
                                end_sale_date: Optional[date] = None,
                                payment_method: Optional[str] = None,
                                start_payment_deadline: Optional[date] = None,
                                end_payment_deadline: Optional[date] = None,
                                start_added_date: Optional[date] = None,
                                end_added_date: Optional[date] = None,
                                is_settled: Optional[bool] = None,
                                is_issued: Optional[bool] = None,
                                in_trash: Optional[bool] = None) -> list:
        try:
            stmt = select(Invoice).where(Invoice.user_id == user_id)

            if user_business_entity_id:
                stmt = stmt.where(Invoice.user_business_entity_id == user_business_entity_id)

            if external_business_entity_id:
                stmt = stmt.where(Invoice.external_business_entity_id == external_business_entity_id)

            if invoice_number:
                stmt = stmt.where(Invoice.invoice_number.ilike(f"%{invoice_number}%"))

            if start_issue_date:
                stmt = stmt.where(Invoice.issue_date >= start_issue_date)
            
            if end_issue_date:
                stmt = stmt.where(Invoice.issue_date <= end_issue_date)
            
            if start_sale_date:
                stmt = stmt.where(Invoice.sale_date >= start_sale_date)
            
            if end_sale_date:
                stmt = stmt.where(Invoice.sale_date <= end_sale_date)

            if payment_method:
                stmt = stmt.where(Invoice.payment_method.ilike(f"%{payment_method}%"))

            if start_payment_deadline:
                stmt = stmt.where(Invoice.payment_deadline >= start_payment_deadline)

            if end_payment_deadline:
                stmt = stmt.where(Invoice.payment_deadline <= end_payment_deadline)

            if start_added_date:
                stmt = stmt.where(Invoice.added_date >= start_added_date)

            if end_added_date:
                stmt = stmt.where(Invoice.added_date <= end_added_date)

            if is_settled is not None:
                stmt = stmt.where(Invoice.is_settled == is_settled)
            
            if is_issued is not None:
                stmt = stmt.where(Invoice.is_issued == is_issued)
            
            if in_trash is not None:
                stmt = stmt.where(Invoice.in_trash == in_trash)

            if external_business_entity_name:
                stmt = stmt.where(ExternalBusinessEntity.name.ilike(f"%{external_business_entity_name}%"))
                stmt = stmt.join(ExternalBusinessEntity, ExternalBusinessEntity.id == Invoice.external_business_entity_id)

            if user_business_entity_name:
                stmt = stmt.where(UserBusinessEntity.company_name.ilike(f"%{user_business_entity_name}%"))
                stmt = stmt.join(UserBusinessEntity, UserBusinessEntity.id == Invoice.user_business_entity_id)

            stmt = stmt.limit(items_per_page).offset((page - 1) * items_per_page)

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
                    is_issued=update_invoice.is_issued
                ).
                returning(Invoice)
            )
            updated_invoice = await self.session.scalar(stmt)
            if updated_invoice is None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.update_invoice() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def update_invoice_in_trash_status(self, user_id: str, invoice_id: str, in_trash: bool) -> None:
        try:
            stmt = (
                update(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                    ).
                values(
                in_trash=in_trash
                ).
                returning(Invoice)
            )
            updated_invoice = await self.session.scalar(stmt)
            if updated_invoice is None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.update_invoice_in_trash_status() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def remove_invoice(self, user_id: str, invoice_id: str) -> bool:
        try:
            stmt = (
                delete(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
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
                    (Invoice.is_issued == new_invoice.is_issued) &
                    (Invoice.in_trash is False)
                    )
                )
            invoice = await self.session.scalar(stmt)
            if invoice is None:
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
                    (Invoice.is_issued == update_invoice.is_issued) &
                    (Invoice.in_trash is False)
                    )
                )
            invoice = await self.session.scalar(stmt)
            if invoice is None:
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
            if updated_invoice is None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.update_invoice_file() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
    
    async def remove_invoice_file(self, user_id: str, invoice_id: str) -> None:
        try:
            stmt = (
                update(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                    ).
                values(
                    invoice_pdf=None
                ).
                returning(Invoice)
            )
            removed_invoice_file = await self.session.scalar(stmt)
            if removed_invoice_file is None:
                raise PostgreSQLNotFoundError("Invoice with provided id not found in database.")
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.remove_invoice_file() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def count_invoices_related_to_user_business_entity(self, user_id: str, user_business_entity_id: str) -> int:
        try:
            stmt = (
                select(func.count()).
                select_from(Invoice).
                where(
                    Invoice.user_business_entity_id == user_business_entity_id,
                    Invoice.user_id == user_id
                    )
            )
            number_of_invoices: int = await self.session.scalar(stmt)
            return number_of_invoices
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.count_invoices_related_to_user_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def count_invoices_related_to_external_business_entity(self, user_id: str, external_business_entity_id: str) -> int:
        try:
            stmt = (
                select(func.count()).
                select_from(Invoice).
                where(
                    Invoice.external_business_entity_id == external_business_entity_id,
                    Invoice.user_id == user_id
                    )
            )
            number_of_invoices: int = await self.session.scalar(stmt)
            return number_of_invoices
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"InvoicePostgresRepository.count_invoices_related_to_external_business_entity() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")