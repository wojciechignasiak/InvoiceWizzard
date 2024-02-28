from app.documents.report_builder_abc import ReportBuilderABC
from app.models.report_model import UserBusinessEntityReportModel, InvoiceReportModel
from app.logging import logger
from datetime import date

class ReportBuilder(ReportBuilderABC):

    async def create_report_html_document(self, 
                                        user_business_entities_report: list[UserBusinessEntityReportModel],
                                        start_date: date,
                                        end_date: date) -> str:
        try:
            report: str = ""
            report = await self._construct_report_html(
                user_business_entities_report,
                start_date,
                end_date
            )
            
            return report
        except Exception as e:
            logger.error(f"ReportBuilder.create_report_html_document() Error: {e}")

    async def _construct_report_html(self,
                                    user_business_entities_report: list[UserBusinessEntityReportModel],
                                    start_date: str,
                                    end_date: str) -> str:
        try:
            styles: str = await self._css_styles()
            report_header: str = await self._create_report_header(
                start_date=start_date,
                end_date=end_date
            )
            report_body: str = ""
            for company in user_business_entities_report:
                report: str = await self._construct_invoice_body_for_company(company)
                report_body += report

            
            report_html = f"""
            <!DOCTYPE html>
            <html>
                {styles}
                <body>
                <div class="invoice-header">
                    {report_header}
                </div>
                <div class="invoice-main">
                    {report_body}
                </div>
                </body>
            </html>
            """
            return report_html
        except Exception as e:
            logger.error(f"ReportBuilder._construct_report_html() Error: {e}")

    async def _construct_invoice_body_for_company(self, company_report: UserBusinessEntityReportModel) -> str:
        try:
            company_header: str = await self._create_report_company_header(company_report.name)
            issued_invoice_summary: str = await self._create_company_issued_invoice_summary(
                sum_of_issued_invoices=company_report.number_of_issued_invoices,
                net_sum_value=company_report.issued_net_value,
                gross_sum_value=company_report.issued_gross_value
            )
            recived_invoice_summary: str = await self._create_company_recived_invoice_summary(
                sum_of_recived_invoices=company_report.number_of_recived_invoices,
                net_value=company_report.recived_net_value,
                gross_value=company_report.recived_gross_value
            )
            issued_unsettled_invoices: str = await self._create_unsettled_invoices_issued(
                    company_report.issued_unsettled_invoices
            )
            unsettled_recived_invoices: str = await self._create_unsettled_recived_invoices(
                company_report.recived_unsettled_invoices
            )
            settled_issued_invoices: str = await self._create_settled_issued_invoices(
                company_report.issued_settled_invoices
            )
            settled_recived_invoices: str = await self._create_settled_recived_invoices(
                company_report.recived_settled_invoices
            )
            invoice_body: str = f"""
            <div class="invoice-raport-element">
            {company_header}
            {issued_invoice_summary}
            {recived_invoice_summary}
            {issued_unsettled_invoices}
            {unsettled_recived_invoices}
            {settled_issued_invoices}
            {settled_recived_invoices}
            </div>
            """
            return invoice_body
        except Exception as e:
            logger.error(f"ReportBuilder._construct_invoice_body_for_company() Error: {e}")

    async def _create_report_company_header(self, company_name: str) -> str:
        try:
            company_header: str = f"""
            <div class="invoice-raport-company-header">
                <span class="invoice-company-title">Nazwa Firmy:</span>
                <span class="invoice-company-name">{company_name}</span>
            </div>
            """
            return company_header
        except Exception as e:
            logger.error(f"ReportBuilder._create_report_company_header() Error: {e}")

    async def _create_company_issued_invoice_summary(self, 
                                                    sum_of_issued_invoices: int,
                                                    net_sum_value: float,
                                                    gross_sum_value: float) -> str:
        try:
            company_issued_invoice_summary: str = f"""
                <div class="invoice-raport-details">
                    <div class="invoice-raport-details-entry">
                        <span class="invoice-raport-details-entry-title">Suma wystawionych faktur</span>
                        <span class="invoice-raport-details-entry-data">{sum_of_issued_invoices}</span>
                    </div>
                    <div class="invoice-raport-details-entry">
                        <span class="invoice-raport-details-entry-title">Suma wartości netto</span>
                        <span class="invoice-raport-details-entry-data">{net_sum_value} PLN</span>
                    </div>
                    <div class="invoice-raport-details-entry">
                        <span class="invoice-raport-details-entry-title">Suma wartości brutto</span>
                        <span class="invoice-raport-details-entry-data">{gross_sum_value} PLN</span>
                    </div>
                </div>"""
            return company_issued_invoice_summary
        except Exception as e:
            logger.error(f"ReportBuilder._create_company_issued_invoice_summary() Error: {e}")

    async def _create_company_recived_invoice_summary(self,
                                                    sum_of_recived_invoices: int,
                                                    net_value: float,
                                                    gross_value: float,
                                                    ) -> str:
        try:
            company_recived_invoice_summary: str = f"""
                    <div class="invoice-raport-details">
                        <div class="invoice-raport-details-entry">
                            <span class="invoice-raport-details-entry-title">Suma otrzymanych faktur</span>
                            <span class="invoice-raport-details-entry-data">{sum_of_recived_invoices}</span>
                        </div>
                        <div class="invoice-raport-details-entry">
                            <span class="invoice-raport-details-entry-title">Suma wartości netto</span>
                            <span class="invoice-raport-details-entry-data">{net_value} PLN</span>
                        </div>
                        <div class="invoice-raport-details-entry">
                            <span class="invoice-raport-details-entry-title">Suma wartości brutto</span>
                            <span class="invoice-raport-details-entry-data">{gross_value} PLN</span>
                        </div>
                    </div>"""
            return company_recived_invoice_summary
        except Exception as e:
            logger.error(f"ReportBuilder._create_company_recived_invoice_summary() Error: {e}")

    async def _create_unsettled_invoices_issued(self, issued_unsettled_invoices: list[InvoiceReportModel]) -> str:
        try:
            invoice_data: str = ""
            index: int = 1
            
            for invoice in issued_unsettled_invoices:
                invoice_data += f"""
                    <tr>
                        <td>{index}</td>
                        <td>{invoice.invoice_number}</td>
                        <td>{invoice.payment_deadline} r.</td>
                        <td>{invoice.net_value} PLN</td>
                        <td>{invoice.gross_value} PLN</td>
                        <td>{invoice.name}</td>
                    </tr>
                """
                index += 1

            unsettled_invoices_issued = f"""
                <div class="invoice-products-table-wrapper">
                        <span class="invoice-table-title">Wystawione faktury nieuregulowane</span>
                        <table>
                            <thead>
                                <tr>
                                    <th>Lp.</th>
                                    <th>Nr. Faktury</th>
                                    <th>Termin Płatności</th>
                                    <th>Kwota Netto</th>
                                    <th>Kwota Brutto</th>
                                    <th>Kontrahent</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoice_data}
                            </tbody>
                        </table>
                    </div>
                    """
            return unsettled_invoices_issued
        except Exception as e:
            logger.error(f"ReportBuilder._create_unsettled_invoices_issued() Error: {e}")

    async def _create_unsettled_recived_invoices(self, recived_unsettled_invoices: list[InvoiceReportModel]) -> str:
        try:
            invoice_data: str = ""
            index: int = 1
            
            for invoice in recived_unsettled_invoices:
                invoice_data += f"""
                    <tr>
                        <td>{index}</td>
                        <td>{invoice.invoice_number}</td>
                        <td>{invoice.payment_deadline} r.</td>
                        <td>{invoice.net_value} PLN</td>
                        <td>{invoice.gross_value} PLN</td>
                        <td>{invoice.name}</td>
                    </tr>
                """
                index += 1
            unsettled_recived_invoices: str = f"""
                <div class="invoice-products-table-wrapper">
                    <span class="invoice-table-title">Otrzymane faktury nieuregulowane</span>
                    <table>
                        <thead>
                            <tr>
                                <th>Lp.</th>
                                <th>Nr. Faktury</th>
                                <th>Termin Płatności</th>
                                <th>Kwota Netto</th>
                                <th>Kwota Brutto</th>
                                <th>Kontrahent</th>
                            </tr>
                        </thead>
                        <tbody>
                            {invoice_data}
                        </tbody>
                    </table>
                </div>"""
            return unsettled_recived_invoices
        except Exception as e:
            logger.error(f"ReportBuilder._create_unsettled_recived_invoices() Error: {e}")

    async def _create_settled_issued_invoices(self, settled_issued_invoices: list[InvoiceReportModel]) -> str:
        try:
            invoice_data: str = ""
            index: int = 1
            
            for invoice in settled_issued_invoices:
                invoice_data += f"""
                    <tr>
                        <td>{index}</td>
                        <td>{invoice.invoice_number}</td>
                        <td>{invoice.payment_deadline} r.</td>
                        <td>{invoice.net_value} PLN</td>
                        <td>{invoice.gross_value} PLN</td>
                        <td>{invoice.name}</td>
                    </tr>
                """
                index += 1

            
            settled_issued_invoices_body: str = f"""
                <div class="invoice-products-table-wrapper">
                    <span class="invoice-table-title">Wystawione faktury uregulowane</span>
                    <table>
                        <thead>
                            <tr>
                                <th>Lp.</th>
                                <th>Nr. Faktury</th>
                                <th>Termin Płatności</th>
                                <th>Kwota Netto</th>
                                <th>Kwota Brutto</th>
                                <th>Kontrahent</th>
                            </tr>
                        </thead>
                        <tbody>
                            {invoice_data}
                        </tbody>
                    </table>
                </div>"""
            return settled_issued_invoices_body
        except Exception as e:
            logger.error(f"ReportBuilder._create_settled_issued_invoices() Error: {e}")

    async def _create_settled_recived_invoices(self, settled_recived_invoices: list[InvoiceReportModel]) -> str:
        try:
            invoice_data: str = ""
            index: int = 1
            
            for invoice in settled_recived_invoices:
                invoice_data += f"""
                    <tr>
                        <td>{index}</td>
                        <td>{invoice.invoice_number}</td>
                        <td>{invoice.payment_deadline} r.</td>
                        <td>{invoice.net_value} PLN</td>
                        <td>{invoice.gross_value} PLN</td>
                        <td>{invoice.name}</td>
                    </tr>
                """
                index += 1

            settled_recived_invoices_body = f"""
                <div class="invoice-products-table-wrapper">
                    <span class="invoice-table-title">Otrzymane faktury uregulowane</span>
                    <table>
                        <thead>
                            <tr>
                                <th>Lp.</th>
                                <th>Nr. Faktury</th>
                                <th>Termin Płatności</th>
                                <th>Kwota Netto</th>
                                <th>Kwota Brutto</th>
                                <th>Kontrahent</th>
                            </tr>
                        </thead>
                        <tbody>
                            {invoice_data}
                        </tbody>
                    </table>
                </div>"""
            
            return settled_recived_invoices_body
        except Exception as e:
            logger.error(f"ReportBuilder._create_settled_recived_invoices() Error: {e}")

    async def _create_report_header(self, 
                                    start_date: date, 
                                    end_date: date) -> str:
        try:
            report_header: str = f"""
                <div class="invoice-title">
                    <span class="invoice-header-title">Raport faktur</span>
                    <span class="invoice-header-subtitle">z przedziału czasowego</span>
                </div>
                <div class="invoice-header-data">
                    <span class="invoice-header-date">{start_date} r.</span>
                    <span class="invoice-header-dates-separator">−</span>
                    <span class="invoice-header-date"> {end_date} r.</span>
                </div>
            """
            return report_header
        except Exception as e:
            logger.error(f"ReportBuilder._create_report_header() Error: {e}")

    async def _css_styles(self) -> str:
        styles: str = """
            <head>
                <meta charset="UTF-8">
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&family=Sora:wght@100;200;300;400;500;600;700;800&display=swap');
                    *{
                        box-sizing: border-box;
                        font-family: 'Roboto', sans-serif;
                    }
                    body{
                        background-color: #999;
                        margin: 0;
                        padding: 0;
                        width: fit-content;
                        height: fit-content;
                    }
                    .invoice-main{
                        width: 800px;
                        background: #fff;
                        min-height: 100vh;
                    }
                    .invoice-raport-element{
                        display: flex;
                        flex-direction: column;
                        padding: 25px;
                    }
                    
                    .invoice-raport-element:not(:last-child){
                        padding-bottom: 0px;
                    }
                    .invoice-raport-element:not(:last-child)::after{
                        content: " ";
                        width: 100%;
                        height: 1px;
                        margin: 25px 0px 0px 0px;
                        background-color: #1F1F1F;
                        opacity: 50%;
                    }
                    .invoice-header{
                        width: 100%;
                        padding: 20px;
                        background-color: #1F1F1F;
                        color: #fff;
                    }
                    .invoice-title{
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        width: 100%;
                        margin-bottom: 10px;
                    }
                    .invoice-header-title{
                        display: block;
                        text-transform: uppercase;
                        font-size: 48px;
                        font-weight: 900;
                        
                    }
                    .invoice-header-subtitle{
                        display: block;
                        text-transform: uppercase;
                        font-size: 24px;
                        font-weight: 600;
                        
                    }
                    .invoice-header-data-content{
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                    }
                    .invoice-header-data{
                        display: flex;
                        flex-direction: row;
                        justify-content: center;
                        align-items: center;
                        width: 100%;
                    }
                    .invoice-header-dates-separator{
                        font-weight: 600;
                        margin: 0px 8px 0px 8px;
                    }
                    .invoice-entry-title{
                        font-weight: 600;
                    }
                    .invoice-header-date{
                        font-weight: 300;
                        text-transform: lowercase;
                    }
                    .invoice-table-title{
                        font-weight: 600;
                        text-transform: uppercase;
                        display: block;
                        font-size: 14px;
                        margin-bottom: 10px;
                    }
                    .invoice-products-table-wrapper{
                        width: 100%;
                        margin-top: 25px;
                    }
                    
                    .invoice-products-table-wrapper table{
                        width: 100%;
                        font-size: 14px;
                        border-collapse: collapse;
                        border-left: #1F1F1F 1px solid;
                        border-right: #1F1F1F 1px solid;
                    }
                    .invoice-products-table-wrapper thead{
                        background-color: #1F1F1F;
                        color: #fff;
                        border-left: #1F1F1F 1px solid;
                        border-right: #1F1F1F 1px solid;
                    }
                    .invoice-products-table-wrapper th{
                        padding: 8px;
                    }
                    .invoice-products-table-wrapper td{
                        padding: 8px;
                        text-align: center;
                        border-bottom: solid 1px #1F1F1F;
                    }
                    .invoice-products-table-wrapper tbody > tr:nth-child(even){
                        background-color: #f0f0f0;
                    }
                    .invoice-raport-detials-content{
                        width: 100%;    
                    }
                    .invoice-raport-details:first-child{
                        margin-bottom: 25px;
                    }
                    .invoice-raport-details{
                        width: 100%;
                        background-color: #f0f0f0;
                        color: #1F1F1F;
                        border-radius: 8px;
                        display: flex;
                        flex-direction: row;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .invoice-raport-details-entry{
                        padding: 16px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    }
                    .invoice-raport-details-entry-title{
                        text-transform: uppercase;
                        font-weight: 700;
                    }
                    .invoice-raport-details-entry-data{
                        font-weight: 300;
                    }
                    .invoice-raport-company-header{
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        justify-content: flex-start;
                        padding-bottom: 25px;
                    }
                    .invoice-company-title{
                        font-weight: 800;
                        font-size: 24px;
                        margin-right: 8px;
                    }
                    .invoice-company-name{
                        font-weight: 400;
                        font-size: 24px;
                    }
                </style>
            </head>
            """
        
        return styles