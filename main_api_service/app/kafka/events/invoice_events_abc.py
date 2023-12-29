from abc import ABC, abstractmethod


class InvoiceEventsABC(ABC):

    @abstractmethod
    async def remove_invoice(
        self, 
        id: str, 
        email_address: str, 
        invoice_number: str,
        user_company_name: str,
        external_business_entity_name: str,
        is_issued: bool):
        ...
        
    @abstractmethod
    async def invoice_removed(
        self, 
        id: str, 
        email_address: str, 
        invoice_number: str,
        user_company_name: str,
        external_busines_entity_name: str,
        is_issued: bool):
        ...