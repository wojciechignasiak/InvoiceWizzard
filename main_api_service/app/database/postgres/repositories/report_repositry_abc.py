from abc import ABC, abstractmethod
from datetime import date

class ReportPostgresRepositoryABC(ABC):

    @abstractmethod
    async def get_user_business_entities_net_and_gross_values(
            self,
            user_id: str,
            start_date: date, 
            end_date: date, 
            is_issued: bool) -> list:
        ...

    @abstractmethod
    async def get_user_business_entity_number_of_invoices(
            self,
            user_id: str,
            start_date: str, 
            end_date: str, 
            is_issued: bool,
            user_business_entity_id: str) -> list[tuple]:
        ...

    @abstractmethod
    async def get_user_invoice_data_related_to_user_business_entity(
            self,
            user_id: str,
            user_business_entity_id: str,
            start_date: str, 
            end_date: str, 
            is_issued: bool,
            is_settled: bool) -> list[tuple]:
        ...