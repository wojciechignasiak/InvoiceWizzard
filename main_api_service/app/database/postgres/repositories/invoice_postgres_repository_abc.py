from abc import ABC, abstractmethod
from typing import Optional
from app.models.invoice_model import CreateInvoiceManuallyModel, UpdateInvoiceModel 
from app.schema.schema import Invoice

class InvoicePostgresRepositoryABC(ABC):
    
    @abstractmethod
    async def create_invoice_manually(user_id: str, invoice_pdf_location: str, new_invoice: CreateInvoiceManuallyModel) -> Invoice:
        pass

    @abstractmethod
    async def get_invoice(self, user_id: str, invoice_id: str) -> Invoice:
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def update_invoice(self, user_id: str, update_invoice: UpdateInvoiceModel) -> Invoice:
        pass

    @abstractmethod
    async def remove_invoice(self, user_id: str, invoice_id: str) -> bool:
        pass