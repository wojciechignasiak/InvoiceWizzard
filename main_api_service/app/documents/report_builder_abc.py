from abc import ABC, abstractmethod
from app.models.report_model import UserBusinessEntityReportModel, InvoiceReportModel
from datetime import date


class ReportBuilderABC(ABC):

    @abstractmethod
    async def create_report_html_document(self, 
                                        user_business_entities_report: list[UserBusinessEntityReportModel],
                                        start_date: date,
                                        end_date: date) -> str:
        ...

    @abstractmethod
    async def _construct_report_html(self,
                                    user_business_entities_report: list[UserBusinessEntityReportModel],
                                    start_date: date,
                                    end_date: date) -> str:
        ...

    @abstractmethod
    async def _css_styles(self) -> str:
        ...

    @abstractmethod
    async def _construct_invoice_body_for_company(self, company_report: UserBusinessEntityReportModel) -> str:
        ...

    @abstractmethod
    async def _create_report_company_header(self, company_name: str) -> str:
        ...

    @abstractmethod
    async def _create_company_issued_invoice_summary(self, 
                                                    sum_of_issued_invoices: int,
                                                    net_sum_value: float,
                                                    gross_sum_value: float) -> str:
        ...
    
    @abstractmethod
    async def _create_company_recived_invoice_summary(self,
                                                    sum_of_recived_invoices: int,
                                                    net_value: float,
                                                    gross_value: float,
                                                    ) -> str:
        ...
    
    @abstractmethod
    async def _create_unsettled_invoices_issued(self, issued_unsettled_invoices: list[InvoiceReportModel]) -> str:
        ...

    @abstractmethod
    async def _create_unsettled_recived_invoices(self, recived_unsettled_invoices: list[InvoiceReportModel]) -> str:
        ...

    @abstractmethod
    async def _create_settled_issued_invoices(self, settled_issued_invoices: list[InvoiceReportModel]) -> str:
        ...
    
    @abstractmethod
    async def _create_settled_recived_invoices(self, settled_recived_invoices: list[InvoiceReportModel]) -> str:
        ...
    
    @abstractmethod
    async def _create_report_header(self, start_date: str, end_date: str) -> str:
        ...

    