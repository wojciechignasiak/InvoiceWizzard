from abc import ABC, abstractmethod
from app.models.invoice_model import CreateInvoiceManuallyModel
from app.schema.schema import Invoice

class InvoicePostgresRepositoryABC(ABC):
    
    @abstractmethod
    async def create_invoice_manually(user_id: str, invoice_pdf_location: str, new_invoice: CreateInvoiceManuallyModel) -> Invoice:
        pass

    @abstractmethod
    async def get_invoice(user_id: str, invoice_id: str) -> Invoice:
        pass

    @abstractmethod
    async def get_all_invoices(user_id: str) -> list:
        pass

    @abstractmethod
    async def update_invoice():
        pass

    @abstractmethod
    async def remove_invoice(user_id: str, invoice_id: str) -> bool:
        pass