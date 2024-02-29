from abc import ABC, abstractmethod
from typing import Union


class InvoiceBuilderABC(ABC):

    @abstractmethod
    async def create_invoice_html_document(self) -> str:
        ...

    @abstractmethod
    async def _construct_invoice_html(self,
                                    styles: str, 
                                    seller_data: str,
                                    invoice_number: str,
                                    issue_date: str,
                                    sale_date: str,
                                    payment_method: str,
                                    payment_deadline: str,
                                    buyer: str,
                                    invoice_items: str,
                                    gross_sum: str,
                                    notes: Union[str, None] = None) -> str:
        ...

    @abstractmethod
    async def _css_styles(self) -> str:
        ...

    @abstractmethod
    async def _seller_html(self) -> str:
        ...

    @abstractmethod
    async def _buyer_html(self, buyer_nip: Union[str, None] = None) -> str:
        ...

    @abstractmethod
    async def _buyer_nip_html(self) -> str:
        ...

    @abstractmethod
    async def _invoice_number_html(self) -> str:
        ...

    @abstractmethod
    async def _issue_date_html(self) -> str:
        ...

    @abstractmethod
    async def _sale_date_html(self) -> str:
        ...

    @abstractmethod
    async def _payment_deadline_html(self) -> str:
        ...

    @abstractmethod
    async def _payment_method_html(self) -> str:
        ...

    @abstractmethod
    async def _invoice_items_html(self) -> str:
        ...

    @abstractmethod
    async def _count_gross_sum(self) -> float:
        ...

    @abstractmethod
    async def _gross_sum_html(self, gross_sum_value: float) -> str:
        ...

    @abstractmethod
    async def _notes_html(self) -> str:
        ...