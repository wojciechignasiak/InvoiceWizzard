from abc import ABC, abstractmethod


class InvoiceRedisRepositoryABC(ABC):

    @abstractmethod
    async def initialize_invoice_removal(self, key_id: str, invoice_id: str) -> bool:
        pass

    @abstractmethod
    async def retrieve_invoice_removal(self, key_id: str) -> bytes:
        pass

    @abstractmethod
    async def delete_invoice_removal(self, key_id: str) -> bool:
        pass