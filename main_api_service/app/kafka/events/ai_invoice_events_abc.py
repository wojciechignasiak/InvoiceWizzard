from abc import ABC, abstractmethod


class AIInvoiceEventsABC(ABC):

    @abstractmethod
    async def extract_invoice_data(self, file_location: str):
        ...