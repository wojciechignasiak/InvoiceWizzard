from app.database.postgres.repositories.base_postgres_repository import BasePostgresRepository
from app.database.postgres.repositories.invoice_item_repository_abc import InvoiceItemPostgresRepositoryABC
from app.models.invoice_model import CreateInvoiceItemModel, UpdateInvoiceItemModel
from app.schema.schema import InvoiceItem
from app.logging import logger
from uuid import uuid4, UUID

class InvoiceItemPostgresRepository(BasePostgresRepository, InvoiceItemPostgresRepositoryABC):
    
    async def create_invoice_item(self, user_id: str, invoice_id: str, new_invoice_item: CreateInvoiceItemModel) -> InvoiceItem:
        pass

    async def get_invoice_item(self, user_id: str, invoice_item_id: str) -> InvoiceItem:
        pass

    async def get_invoice_items_from_invoice(self, user_id: str, invoice_id: str) -> list:
        pass

    async def update_invoice_item(self, user_id: str, update_invoice_item: UpdateInvoiceItemModel) -> InvoiceItem:
        pass

    async def remove_invoice_item(self, user_id: str, invoice_item_id: str) -> bool:
        pass