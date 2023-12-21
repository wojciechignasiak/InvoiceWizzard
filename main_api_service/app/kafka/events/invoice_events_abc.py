from abc import ABC, abstractmethod


class InvoiceEventsABC(ABC):

    @abstractmethod
    async def remove_invoice(self, id: str, email_address: str, user_business_entity_name: str):
        ...
        
    @abstractmethod
    async def invoice_removed(self, email_address: str, user_business_entity_name: str):
        ...