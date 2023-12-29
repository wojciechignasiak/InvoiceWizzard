from abc import ABC, abstractmethod
from typing import Optional
from app.models.invoice_model import CreateInvoiceModel, UpdateInvoiceModel 
from app.schema.schema import Invoice

class InvoicePostgresRepositoryABC(ABC):
    
    @abstractmethod
    async def create_invoice(self, user_id: str, new_invoice: CreateInvoiceModel) -> Invoice:
        ...

    @abstractmethod
    async def get_invoice(self, user_id: str, invoice_id: str) -> Invoice:
        ...

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
                                is_issued: Optional[bool] = None,
                                in_trash: Optional[bool] = None) -> list:
        ...

    @abstractmethod
    async def update_invoice(self, user_id: str, update_invoice: UpdateInvoiceModel) -> None:
        ...

    @abstractmethod
    async def update_invoice_in_trash_status(self, user_id: str, invoice_id: str, in_trash: bool) -> None:
        ...

    @abstractmethod
    async def remove_invoice(self, user_id: str, invoice_id: str) -> bool:
        ...

    @abstractmethod
    async def is_invoice_unique(self, user_id: str, new_invoice: CreateInvoiceModel) -> bool:
        ...

    @abstractmethod
    async def is_invoice_unique_beside_one_to_update(self, user_id: str, update_invoice: UpdateInvoiceModel) -> bool:
        ...

    @abstractmethod
    async def update_invoice_file(self, user_id: str, invoice_id: str, invoice_pdf_location: str) -> None:
        ...
    
    @abstractmethod
    async def remove_invoice_file(self, user_id: str, invoice_id: str) -> None:
        ...

    @abstractmethod
    async def count_invoices_related_to_user_business_entity(self, user_id: str, user_business_entity_id: str) -> int:
        ...
        
    @abstractmethod
    async def count_invoices_related_to_external_business_entity(self, user_id: str, external_business_entity_id: str) -> int:
        ...