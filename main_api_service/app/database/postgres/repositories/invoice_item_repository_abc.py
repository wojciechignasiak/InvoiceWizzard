from abc import ABC, abstractmethod
from app.models.invoice_item_model import CreateInvoiceItemModel, UpdateInvoiceItemModel
from app.schema.schema import InvoiceItem

class InvoiceItemPostgresRepositoryABC(ABC):
    
    @abstractmethod
    async def create_invoice_item(self, user_id: str, invoice_id: str, new_invoice_item: CreateInvoiceItemModel) -> InvoiceItem:
        ...

    @abstractmethod
    async def get_invoice_item(self, user_id: str, invoice_item_id: str) -> InvoiceItem:
        ...

    @abstractmethod
    async def get_invoice_items_by_invoice_id(self, user_id: str, invoice_id: str) -> list:
        ...

    @abstractmethod
    async def update_invoice_item(self, user_id: str, update_invoice_item: UpdateInvoiceItemModel) -> InvoiceItem:
        ...

    @abstractmethod
    async def remove_invoice_item(self, user_id: str, invoice_item_id: str) -> bool:
        ...