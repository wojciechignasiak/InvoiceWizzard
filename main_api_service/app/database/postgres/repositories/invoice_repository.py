#internal modules
from main_api_service.app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from main_api_service.app.custom_exceptions.custom_exceptions import DatabaseError
from main_api_service.app.models.invoice_model import CreateInvoiceModel, UpdateInvoiceModel
from main_api_service.app.models.invoice_item_model import CreateInvoiceItemModel
from main_api_service.app.schema.schema import Invoice, ExternalBusinessEntity, UserBusinessEntity, InvoiceItem

#3rd party modules
from fastapi import status
from sqlalchemy import insert, select, update, delete, func, ScalarResult
from sqlalchemy.sql import Select

#1st party modules
from typing import Protocol
from datetime import date
from uuid import UUID

class IInvoicePostgresRepository(Protocol):

    async def create_invoice(self, invoice_id: UUID, user_id: UUID, new_invoice: CreateInvoiceModel) -> None:
        ...

    async def create_invoice_item(self, user_id: UUID, invoice_id: UUID, invoice_item_id: UUID, new_invoice_item: CreateInvoiceItemModel) -> None:
        ...

    async def get_invoice_by_invoice_number(self, user_id: UUID, invoice_number: str) -> tuple[Invoice] | tuple:
        ...

    async def get_invoice_by_id(self, user_id: UUID, invoice_id: UUID) -> Invoice | None:
        ...

    async def get_invoice_items_by_invoice_id(self, user_id: UUID, invoice_id: UUID, in_trash: bool) -> tuple[InvoiceItem] | tuple:
        ...

    async def get_invoice_items_for_multiple_invoices_by_invoice_id(self, user_id: UUID, invoices_id: tuple[UUID, ...],
                                                                    in_trash: bool) -> tuple[InvoiceItem] | tuple:
        ...

    async def get_all_invoices(
            self,
            user_id: UUID,
            page: int = 1,
            items_per_page: int = 10,
            user_business_entity_id: UUID | None = None,
            user_business_entity_name: str | None = None,
            external_business_entity_id: UUID | None = None,
            external_business_entity_name: str | None = None,
            invoice_number: str | None = None,
            start_issue_date: date | None = None,
            end_issue_date: date | None = None,
            start_sale_date: date | None = None,
            end_sale_date: date | None = None,
            payment_method: str | None = None,
            start_payment_deadline: date | None = None,
            end_payment_deadline: date | None = None,
            start_added_date: date | None = None,
            end_added_date: date | None = None,
            is_settled: bool | None = None,
            is_issued: bool | None = None,
            in_trash: bool | None = None
    ) -> tuple[Invoice] | tuple:
        ...

    async def update_invoice(self, user_id: UUID, update_invoice: UpdateInvoiceModel) -> None:
        ...

    async def update_invoice_in_trash_status(self, user_id: UUID, invoice_id: UUID, in_trash: bool) -> None:
        ...

    async def update_invoice_items_in_trash_status(self, user_id: UUID, invoice_id: UUID, in_trash: bool) -> None:
        ...

    async def remove_invoice(self, user_id: UUID, invoice_id: UUID) -> None:
        ...

    async def update_invoice_file_status(self, user_id: UUID, invoice_id: UUID, invoice_file_status: bool) -> None:
        ...

    async def count_invoices_related_to_user_business_entity(self, user_id: UUID, user_business_entity_id: UUID) -> int:
        ...

    async def count_invoices_related_to_external_business_entity(self, user_id: UUID,
                                                                 external_business_entity_id: UUID) -> int:
        ...

async def new_invoice_postgres_repository() -> IInvoicePostgresRepository:
    try:
        return InvoicePostgresRepository()
    except Exception as e:
        raise DatabaseError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Unexpected error occurred while creating invoice repository.",
            argument=None,
            child_error=e
        )

class InvoicePostgresRepository(BasePostgresRepository, IInvoicePostgresRepository):
    
    async def create_invoice(self, invoice_id: UUID, user_id: UUID, new_invoice: CreateInvoiceModel) -> None:
        try:
            stmt = (
                insert(Invoice).
                values(
                    id=invoice_id,
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
                )
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while creating new invoice in sql database.",
                argument={'user_id': user_id, 'new_invoice': new_invoice},
                child_error=e
            )

    async def create_invoice_item(self, user_id: UUID, invoice_id: UUID, invoice_item_id: UUID, new_invoice_item: CreateInvoiceItemModel) -> None:
        try:
            stmt = (
                insert(InvoiceItem).
                values(
                    id=invoice_item_id,
                    user_id=user_id,
                    invoice_id=invoice_id,
                    item_description=new_invoice_item.item_description,
                    number_of_items=new_invoice_item.number_of_items,
                    net_value=new_invoice_item.net_value,
                    gross_value=new_invoice_item.gross_value
                )
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while creating new invoice item in sql database.",
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'invoice_item_id': invoice_item_id, 'new_invoice_item': new_invoice_item},
                child_error=e
            )
    
    async def get_invoice_by_id(self, user_id: UUID, invoice_id: UUID) -> Invoice | None:
        try:
            stmt: Select = (
                select(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                )
            )
            invoice: Invoice | None = await self.session.scalar(stmt)

            return invoice
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting invoice from sql database.",
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e
            )

    async def get_invoice_by_invoice_number(self, user_id: UUID, invoice_number: str) -> tuple[Invoice] | tuple:
        try:
            stmt: Select = select(Invoice).where(Invoice.invoice_number == invoice_number, Invoice.user_id == user_id)
            result: ScalarResult[Invoice | None] = await self.session.scalars(stmt)

            return tuple(result.all())
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting invoice by invoice number: {invoice_number} and user id: {user_id} from sql database.",
                argument={'user_id': user_id, 'invoice_number': invoice_number},
                child_error=e
            )

    async def get_invoice_items_by_invoice_id(self, user_id: UUID, invoice_id: UUID, in_trash: bool) -> tuple[InvoiceItem] | tuple:
        try:
            stmt = (
                select(InvoiceItem).
                where(
                    InvoiceItem.invoice_id == invoice_id,
                    InvoiceItem.user_id == user_id,
                    InvoiceItem.in_trash == in_trash
                )
            )
            invoice_items: ScalarResult[InvoiceItem | None] = await self.session.scalars(stmt)

            return tuple(invoice_items.all())
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting invoice items by invoice id: {invoice_id} and user id: {user_id} from sql database.",
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'in_trash': in_trash},
                child_error=e
            )

    async def get_all_invoices(
            self,
            user_id: UUID,
            page: int = 1,
            items_per_page: int = 10,
            user_business_entity_id: UUID | None = None,
            user_business_entity_name: str | None = None,
            external_business_entity_id: UUID | None = None,
            external_business_entity_name: str | None = None,
            invoice_number: str | None = None,
            start_issue_date: date | None = None,
            end_issue_date: date | None = None,
            start_sale_date: date | None = None,
            end_sale_date: date | None = None,
            payment_method: str | None = None,
            start_payment_deadline: date | None = None,
            end_payment_deadline: date | None = None,
            start_added_date: date | None = None,
            end_added_date: date | None = None,
            is_settled: bool | None = None,
            is_issued: bool | None = None,
            in_trash: bool | None = None
    ) -> tuple[Invoice] | tuple:
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
                stmt = stmt.join(ExternalBusinessEntity,
                                 ExternalBusinessEntity.id == Invoice.external_business_entity_id)

            if user_business_entity_name:
                stmt = stmt.where(UserBusinessEntity.company_name.ilike(f"%{user_business_entity_name}%"))
                stmt = stmt.join(UserBusinessEntity, UserBusinessEntity.id == Invoice.user_business_entity_id)

            stmt = stmt.limit(items_per_page).offset((page - 1) * items_per_page)

            invoices: ScalarResult[Invoice | None] = await self.session.scalars(stmt)
            return tuple(invoices.all())
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting all user_id: {user_id} invoices from sql database.",
                argument={
                    'user_id': user_id,
                    'page': page,
                    'items_per_page': items_per_page,
                    'user_business_entity_id': user_business_entity_id,
                    'user_business_entity_name': user_business_entity_name,
                    'external_business_entity_id': external_business_entity_id,
                    'external_business_entity_name': external_business_entity_name,
                    'invoice_number': invoice_number,
                    'start_issue_date': start_issue_date,
                    'end_issue_date': end_issue_date,
                    'start_sale_date': start_sale_date,
                    'end_sale_date': end_sale_date,
                    'payment_method': payment_method,
                    'start_payment_deadline': start_payment_deadline,
                    'end_payment_deadline': end_payment_deadline,
                    'start_added_date': start_added_date,
                    'end_added_date': end_added_date,
                    'is_settled': is_settled,
                    'is_issued': is_issued,
                    'in_trash': in_trash,
                },
                child_error=e
            )

    async def get_invoice_items_for_multiple_invoices_by_invoice_id(self, user_id: UUID, invoices_id: tuple[UUID, ...], in_trash: bool) -> tuple[InvoiceItem] | tuple:
        try:
            stmt = (
                select(InvoiceItem).
                where(
                    InvoiceItem.invoice_id.in_(invoices_id),
                    InvoiceItem.user_id == user_id,
                    InvoiceItem.in_trash == in_trash
                )
            )
            invoice_items: ScalarResult[InvoiceItem | None] = await self.session.scalars(stmt)

            return tuple(invoice_items.all())
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while getting invoice items by invoices id: {invoices_id} and user id: {user_id} from sql database.",
                argument={'user_id': user_id, 'invoice_id': invoices_id, 'in_trash': in_trash},
                child_error=e
            )

    async def update_invoice(self, user_id: UUID, update_invoice: UpdateInvoiceModel) -> None:
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
                )
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating invoice with id: {update_invoice.id} and user id: {user_id} from sql database.",
                argument={'user_id': user_id, 'update_invoice': update_invoice,},
                child_error=e
            )
        
    async def update_invoice_in_trash_status(self, user_id: UUID, invoice_id: UUID, in_trash: bool) -> None:
        try:
            stmt = (
                update(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                    ).
                values(
                in_trash=in_trash
                )
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating in trash status of invoice with id: {invoice_id} and user id: {user_id} from sql database.",
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'in_trash': in_trash},
                child_error=e
            )

    async def update_invoice_items_in_trash_status(self, user_id: UUID, invoice_id: UUID, in_trash: bool) -> None:
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
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating in trash status of invoice items with invoice id: {invoice_id} and user id: {user_id} from sql database.",
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'in_trash': in_trash},
                child_error=e
            )

    async def remove_invoice(self, user_id: UUID, invoice_id: UUID) -> None:
        try:
            stmt = (
                delete(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                    )
            )
            await self.session.execute(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while deleting invoice with id: {invoice_id} and user id: {user_id} from sql database.",
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e
            )

        
    async def update_invoice_file_status(self, user_id: UUID, invoice_id: UUID, invoice_file_status: bool) -> None:
        try:
            stmt = (
                update(Invoice).
                where(
                    Invoice.id == invoice_id,
                    Invoice.user_id == user_id
                    ).
                values(
                    invoice_pdf=invoice_file_status
                )
            )
            await self.session.scalar(stmt)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while updating invoice file status by invoice id: {invoice_id} and user id: {user_id} in sql database.",
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'invoice_file_status': invoice_file_status},
                child_error=e
            )

    async def count_invoices_related_to_user_business_entity(self, user_id: UUID, user_business_entity_id: UUID) -> int:
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
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while counting invoices related to user business entity with id: {user_business_entity_id} in sql database.",
                argument={'user_id': user_id, 'user_business_entity_id': user_business_entity_id,},
                child_error=e
            )
        
    async def count_invoices_related_to_external_business_entity(self, user_id: UUID, external_business_entity_id: UUID) -> int:
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
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred while counting invoices related to external business entity with id: {external_business_entity_id} in sql database.",
                argument={'user_id': user_id, 'external_business_entity_id': external_business_entity_id, },
                child_error=e
            )