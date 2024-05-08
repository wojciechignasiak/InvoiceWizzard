from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.report_repositry_abc import ReportPostgresRepositoryABC
from app.database.postgres.exceptions.custom_postgres_exceptions import PostgreSQLDatabaseError
from sqlalchemy import select, func, Result, case
from app.schema.schema import Invoice, InvoiceItem, UserBusinessEntity, ExternalBusinessEntity
from sqlalchemy.exc import (
    DataError, 
    StatementError,
    DatabaseError,
    InterfaceError,
    OperationalError,
    ProgrammingError
    )
from datetime import date
from app.logging import logger
from typing import Optional


class ReportPostgresRepository(BasePostgresRepository, ReportPostgresRepositoryABC):

    async def get_user_business_entities_net_and_gross_values(
            self,
            user_id: str,
            start_date: date, 
            end_date: date) -> list[Optional[tuple[str, float, float, float, float]]]:
        try:
            stmt = (
                select(
                    UserBusinessEntity.id,
                    UserBusinessEntity.company_name,
                    func.sum(
                        case(
                            (Invoice.is_issued is True, InvoiceItem.net_value),
                            else_=0
                        )
                    ).label("issued_invoice_net_value"),
                    func.sum(
                        case(
                            (Invoice.is_issued is True, InvoiceItem.gross_value),
                            else_=0
                        )
                    ).label("issued_invoice_gross_value"),
                    func.sum(
                        case(
                            (Invoice.is_issued is False, InvoiceItem.net_value),
                            else_=0
                        )
                    ).label("received_invoice_net_value"),
                    func.sum(
                        case(
                            (Invoice.is_issued is False, InvoiceItem.gross_value),
                            else_=0
                        )
                    ).label("received_invoice_gross_value")
                )
                .join(Invoice, Invoice.id == InvoiceItem.invoice_id)
                .join(UserBusinessEntity, UserBusinessEntity.id == Invoice.user_business_entity_id)
                .filter(
                    Invoice.in_trash is False,
                    InvoiceItem.in_trash is False,
                    Invoice.issue_date.between(start_date, end_date),
                    UserBusinessEntity.user_id == user_id
                )
                .group_by(UserBusinessEntity.id, UserBusinessEntity.company_name)
            )

            result: Result[tuple[str, float, float, float, float]]  = await self.session.execute(stmt)
            return result.all()
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ReportPostgresRepository.get_invoice_data_for_report() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")
        
    async def get_user_business_entity_number_of_invoices(
            self,
            user_id: str,
            start_date: date, 
            end_date: date, 
            is_issued: bool,
            user_business_entity_id: str) -> list[Optional[tuple[int]]]:
        try:
            stmt = (
                select(
                    func.count(Invoice.id).label("number_of_invoices")
                    )
                .select_from(Invoice)
                .join(UserBusinessEntity, UserBusinessEntity.id == Invoice.user_business_entity_id)
                .filter(Invoice.in_trash is False,
                        Invoice.is_issued is is_issued,
                        Invoice.issue_date.between(start_date, end_date),
                        UserBusinessEntity.id == user_business_entity_id,
                        UserBusinessEntity.user_id == user_id)
            )

            result: Result[Optional[tuple[int]]]  = await self.session.execute(stmt)
            return result.all()
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ReportPostgresRepository.get_invoice_data_for_report() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")

    async def get_user_invoice_data_related_to_user_business_entity(
            self,
            user_id: str,
            user_business_entity_id: str,
            start_date: date, 
            end_date: date, 
            is_issued: bool,
            is_settled: bool) -> list[Optional[tuple[str, date, str, float, float]]]:
        try:
            stmt = (
                select(
                    Invoice.invoice_number,
                    Invoice.payment_deadline, 
                    ExternalBusinessEntity.name,
                    func.sum(InvoiceItem.net_value).label("invoice_net_value"),
                    func.sum(InvoiceItem.gross_value).label("invoice_gross_value"),
                    )
                .join(Invoice, Invoice.id == InvoiceItem.invoice_id)
                .join(ExternalBusinessEntity, ExternalBusinessEntity.id == Invoice.external_business_entity_id)
                .join(UserBusinessEntity, UserBusinessEntity.id == Invoice.user_business_entity_id)
                .filter(Invoice.in_trash is False,
                        Invoice.is_issued is is_issued,
                        Invoice.is_settled is is_settled,
                        InvoiceItem.in_trash is False,
                        UserBusinessEntity.id == user_business_entity_id,
                        Invoice.issue_date.between(start_date, end_date),
                        UserBusinessEntity.user_id == user_id)
                .group_by(Invoice.invoice_number, Invoice.payment_deadline, ExternalBusinessEntity.name)
            )

            result: Result[tuple[str, date, str, float, float]]  = await self.session.execute(stmt)
            return result.all()
        except (DataError, DatabaseError, InterfaceError, StatementError, OperationalError, ProgrammingError) as e:
            logger.error(f"ReportPostgresRepository.get_invoice_data_for_report() Error: {e}")
            raise PostgreSQLDatabaseError("Error related to database occured.")