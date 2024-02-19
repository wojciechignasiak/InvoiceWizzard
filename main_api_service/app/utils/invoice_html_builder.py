from app.models.invoice_item_model import InvoiceItemModel
from app.models.invoice_model import InvoiceModel
from app.models.user_business_entity_model import UserBusinessEntityModel
from app.models.external_business_entity_model import ExternalBusinessEntityModel
from app.logging import logger
from typing import Union
from app.utils.invoice_html_builder_abc import InvoiceHTMLBuilderABC

class InvoiceHTMLBuilder(InvoiceHTMLBuilderABC):
    __slots__= (
        'invoice', 
        'invoice_items',
        'user_business_entity',
        'external_business_entity'
    )
    def __init__(self, 
                invoice: InvoiceModel,
                invoice_items: list[InvoiceItemModel],
                user_business_entity: UserBusinessEntityModel,
                external_business_entity: ExternalBusinessEntityModel):
        
        self.invoice: InvoiceModel = invoice
        self.invoice_items: list[InvoiceItemModel] = invoice_items
        self.user_business_entity: UserBusinessEntityModel = user_business_entity
        self.external_business_entity: ExternalBusinessEntityModel = external_business_entity

    async def create_invoice_html_document(self) -> str:
        try:
            styles: str = await self._css_styles()
            seller_data: str = await self._seller_html()
            invoice_number: str = await self._invoice_number_html()
            issue_date: str = await self._issue_date_html()
            sale_date: str = await self._sale_date_html()
            payment_method: str = await self._payment_method_html()
            payment_deadline: str = await self._payment_deadline_html()
            buyer: str = await self._buyer_html(self.external_business_entity.nip)
            invoice_items: str = await self._invoice_items_html()
            gross_sum_value: float = await self._count_gross_sum()
            gross_sum: str = await self._gross_sum_html(
                gross_sum_value=gross_sum_value)
            notes: Union[str, None] = await self._notes_html()
            if notes:
                constructed_invoice_html = await self._construct_invoice_html(
                    styles = styles,
                    seller_data = seller_data,
                    invoice_number = invoice_number,
                    issue_date = issue_date,
                    sale_date = sale_date,
                    payment_method = payment_method,
                    payment_deadline = payment_deadline,
                    buyer = buyer,
                    invoice_items = invoice_items,
                    gross_sum = gross_sum,
                    notes = notes)
            else:
                constructed_invoice_html = await self._construct_invoice_html(
                    styles = styles,
                    seller_data = seller_data,
                    invoice_number = invoice_number,
                    issue_date = issue_date,
                    sale_date = sale_date,
                    payment_method = payment_method,
                    payment_deadline = payment_deadline,
                    buyer = buyer,
                    invoice_items = invoice_items,
                    gross_sum = gross_sum)
                
            return constructed_invoice_html

        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.create_invoice_html_document() Error: {e}")

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
        try:
            invoice_html = f"""
            <html>
                {styles}
                <body>
                    <div class="invoice-main">
                        <div class="invoice-header">
                            <div class="invoice-title">
                                <span class="invoice-header-title">Faktura</span>
                                {seller_data}
                            </div>
                            <hr />
                            <div class="invoice-header-data">
                                <div>
                                    {invoice_number}
                                    {issue_date}
                                    {sale_date}
                                </div>
                                <div>
                                    {payment_method}
                                    {payment_deadline}
                                </div>
                            </div>
                        </div>
                        {buyer}
                        <div class="invoice-products-table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Lp.</th>
                                        <th>Nazwa towaru/usługi</th>
                                        <th>Ilość szt.</th>
                                        <th>Wartość Netto</th>
                                        <th>VAT %</th>
                                        <th>Wartość Brutto</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {invoice_items}
                                </tbody>
                            </table>
                            {gross_sum}
                            {notes}
                            <div class="invoice-sign-wrapper">
                                <span class="invoice-sign">Osoba upoważniona do odbioru</span>
                                <span class="invoice-sign">Osoba upoważniona do wystawienia</span>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
            """
            return invoice_html
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.construct_invoice() Error: {e}")

    async def _css_styles(self) -> str:
        try:
            styles: str = """
            <head>
                <meta charset="UTF-8">
                <style>
                    *{
                        box-sizing: border-box;
                    }
                    @media print {
                        body {
                            margin: 0;
                        }
                    }
                    @page {
                        margin: 0cm;
                    }
                    body{
                        background: #fff;
                        margin: 0px;
                        padding: 0px;
                        font-family: Arial, Helvetica, sans-serif;
                    }
                    .invoice-main{
                        background: #fff;
                        height: 100%
                    }
                    .invoice-header{
                        width: 100%;
                        padding: 20px;
                        background-color: #f7f7f7;
                        color: #1F1F1F;
                    }
                    .invoice-title{
                        display: flex;
                        align-items: flex-start;
                        justify-content: space-between;
                        width: 100%;
                    }
                    .invoice-header-title{
                        display: flex;
                        font-size: 60px;
                        font-weight: 900;
                    }
                    .invoice-from-data{
                        display: flex;
                        flex-direction: column;
                        font-weight: 300;
                    }
                    .invoice-from-entry{
                        display: block;
                        margin: 3px 0px;
                        font-weight: 300;
                        font-size: 15px;
                    }
                    .invoice-from-entry-title{
                        display: block;
                        font-weight: 600;
                        margin: 3px 0px;
                        font-size: 18px;
                        border-bottom: #1F1F1F25 solid 1px;
                    }
                    hr{
                        opacity: 0;
                    }
                    .invoice-header-data{
                        display: flex;
                        flex-direction: row;
                        justify-content: space-between;
                        align-items: flex-start;
                        width: 100%;
                        padding: 5px 20px 0px 20px;
                    }
                    .invoice-header-data-entry{
                        font-size: 15px;
                        text-transform: uppercase;
                        margin: 10px 0px 10px 0px;
                    }
                    .invoice-entry-title{
                        font-weight: 600;
                    }
                    .invoice-entry{
                        font-weight: 300;
                    }
                    .invoice-client-data{
                        width: 50%;
                        padding: 20px 40px 0px 40px;
                    }
                    .invoice-client-entry-title{
                        display: block;
                        width: 100%;
                        font-weight: 700;
                        margin: 10px 0px;
                        font-size: 18px;
                        border-bottom: #1F1F1F25 solid 1px;
                    }
                    .invoice-client-entry{
                        display: block;
                        margin: 10px 0px;
                        font-weight: 400;
                        font-size: 16px;
                    }
                    .invoice-products-table-wrapper{
                        width: 100%;
                        padding: 40px;
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
                    .invoice-products-payment{
                        margin: 10px 5px;
                        text-align: right;
                        font-size: 18px;
                    }
                    .invoice-products-payment-title{
                        font-weight: 600;
                    }
                    .invoice-products-payment-amount{
                        font-weight: 300;
                    }
                    .invoice-details{
                        width: 100%;
                        margin-top: 30px;
                        padding: 10px;
                        font-size: 14px;
                        min-height: 150px;
                        border: solid 1px #1F1F1F;
                        background-color: #f7f7f7;
                    }
                    .invoice-details-title{
                        display: block;
                        margin-bottom: 5px;
                        width: 100%;
                        font-weight: 600;
                    }
                    .invoice-details-text{
                        display: block;
                        word-wrap: normal;
                        font-weight: 400;
                        padding:0px 5px;
                    }
                    .invoice-sign-wrapper{
                        margin-top: 100px;
                        display: flex;
                        width: 100%;
                        justify-content: space-between;
                    }
                    .invoice-sign{
                        font-size: 10px;
                        border-top: solid 1px #1F1F1F;
                        width: 250px;
                        font-weight: 500;
                        padding-top: 10px;
                        text-align: center;
                        text-transform: uppercase;
                    }
                </style>
            </head>
        """
            return styles
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.css_styles() Error: {e}")

    async def _seller_html(self) -> str:
        try:
            seller = f"""
            <div class="invoice-from-data">
                <span class="invoice-from-entry-title">Sprzedawca</span>
                <span class="invoice-from-entry">{self.user_business_entity.company_name}</span>
                <span class="invoice-from-entry">{self.user_business_entity.street}; {self.user_business_entity.postal_code} {self.user_business_entity.city}</span>
                <span class="invoice-from-entry">NIP {self.user_business_entity.nip}</span>
            </div>
            """
            return seller
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.seller() Error: {e}")

    async def _buyer_html(self, buyer_nip: Union[str, None] = None) -> str:
        try:
            if buyer_nip:
                buyer = f"""
                <div class="invoice-client-data">
                    <span class="invoice-client-entry-title">Nabywca</span>
                    <span class="invoice-client-entry">{self.external_business_entity.name}</span>
                    <span class="invoice-client-entry">{self.external_business_entity.street}; {self.external_business_entity.postal_code} {self.external_business_entity.city}</span>
                    <span class="invoice-client-entry">NIP {buyer_nip}</span>
                </div>
                """
            else:
                buyer = f"""
                <div class="invoice-client-data">
                    <span class="invoice-client-entry-title">Nabywca</span>
                    <span class="invoice-client-entry">{self.external_business_entity.name}</span>
                    <span class="invoice-client-entry">{self.external_business_entity.street}; {self.external_business_entity.postal_code} {self.external_business_entity.city}</span>
                </div>
                """
            return buyer
        except Exception as e:
                logger.error(f"InvoiceHTMLBuilder.buyer() Error: {e}")
    
    async def _buyer_nip_html(self) -> str:
        try:
            buyer_nip = f"""<span class="invoice-client-entry">NIP {self.external_business_entity.nip}</span>"""
            return buyer_nip
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.buyer_nip() Error: {e}")

    async def _invoice_number_html(self) -> str:
        try:
            invoice_number = f"""
            <div class="invoice-header-data-entry">
                <span class="invoice-entry-title">Nr Faktury: </span>
                <span class="invoice-entry">{self.invoice.invoice_number}</span>
            </div>
            """
            return invoice_number
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.invoice_number() Error: {e}")
    
    async def _issue_date_html(self) -> str:
        try:
            issue_date = f"""
            <div class="invoice-header-data-entry">
                <span class="invoice-entry-title">Data wystawienia: </span>
                <span class="invoice-entry">{self.invoice.issue_date}</span>
            </div>
            """
            return issue_date
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.issue_date() Error: {e}")

    async def _sale_date_html(self) -> str:
        try:
            sale_date = f"""
            <div class="invoice-header-data-entry">
                <span class="invoice-entry-title">Data sprzedaży: </span>
                <span class="invoice-entry">{self.invoice.sale_date}</span>
            </div>
            """
            return sale_date
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.sale_date() Error: {e}")

    async def _payment_deadline_html(self) -> str:
        try:
            payment_deadline = f"""
            <div class="invoice-header-data-entry">
                <span class="invoice-entry-title">Termin Płatności: </span>
                <span class="invoice-entry">{self.invoice.payment_deadline}</span>
            </div>
            """
            return payment_deadline
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.payment_deadline() Error: {e}")

    async def _payment_method_html(self) -> str:
        try:
            payment_method = f"""
            <div class="invoice-header-data-entry">
                <span class="invoice-entry-title">Metoda Płatności: </span>
                <span class="invoice-entry">{self.invoice.payment_method}</span>
            </div>
            """
            return payment_method
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.payment_method() Error: {e}")

    async def _invoice_items_html(self) -> str:
        try:
            invoice_items: str = ""
            for ordinal_number, invoice_item in enumerate(self.invoice_items):
                ordinal_number: int = ordinal_number + 1
                item = f"""
                <tr>
                    <td>{ordinal_number}</th>
                    <td>{invoice_item.item_description}</th>
                    <td>{invoice_item.number_of_items}</th>
                    <td>{invoice_item.net_value} PLN</th>
                    <td>{invoice_item.vat_percent} %</th>
                    <td>{invoice_item.gross_value} PLN</th>
                </tr>
                """
                invoice_items += item 
            return invoice_items
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.invoice_items() Error: {e}")

    async def _count_gross_sum(self) -> float:
        try:
            gross_sum: float = 0.0
            for invoice_item in self.invoice_items:
                gross_sum += invoice_item.gross_value
            return gross_sum
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.count_gross_sum() Error: {e}")

    async def _gross_sum_html(self, gross_sum_value: float) -> str:
        try:
            gross_sum = f"""
            <div class="invoice-products-payment">
                <span class="invoice-products-payment-title">Do zapłaty razem:</span>
                <span class="invoice-products-payment-amount">{gross_sum_value} PLN</span>
            </div>
            """
            return gross_sum
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.gross_sum() Error: {e}")

    async def _notes_html(self) -> str:
        try:
            notes = f"""
            <div class="invoice-details">
                <span class="invoice-details-title">Uwagi:</span>
                <span class="invoice-details-text">{self.invoice.notes}</span>
            </div>
            """
            return notes
        except Exception as e:
            logger.error(f"InvoiceHTMLBuilder.notes() Error: {e}")