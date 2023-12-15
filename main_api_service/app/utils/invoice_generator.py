from app.models.invoice_item_model import CreateInvoiceItemModel
from app.models.user_business_entity_model import UserBusinessEntityModel
from app.models.external_business_entity_model import ExternalBusinessEntityModel
from app.logging import logger

async def invoice_generator(
        user_business_entity: UserBusinessEntityModel,
        external_business_entity: ExternalBusinessEntityModel,
        invoice_number,
        issue_date,
        sale_date,
        payment_method,
        payment_deadline,
        notes,
        invoice_items: list[CreateInvoiceItemModel]) -> str:
    try:
        styles = """
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
                        font-family: Arial, Helvetica, sans-serif;
                    }
                    .invoice-main{
                        width: 800px;
                        background: #fff;
                        height: 100vh;
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
                        opacity: 0%;
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
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: flex-start;
                        padding: 20px 40px 0px 40px;
                    }
                    .invoice-client-entry-title{
                        display: block;
                        width: 100%;
                        font-weight: 700;
                        margin: 3px 0px;
                        font-size: 18px;
                        border-bottom: #1F1F1F25 solid 1px;
                    }
                    .invoice-client-entry{
                        display: block;
                        margin: 3px 0px;
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
                        margin-top: 150px;
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
        seller_data_container = f"""
        <div class="invoice-from-data">
            <span class="invoice-from-entry-title">Sprzedawca</span>
            <span class="invoice-from-entry">{user_business_entity.company_name}</span>
            <span class="invoice-from-entry">{user_business_entity.street}; {user_business_entity.postal_code} {user_business_entity.city}</span>
            <span class="invoice-from-entry">NIP {user_business_entity.nip}</span>
        </div>
        """
        invoice_number_container = f"""
        <div class="invoice-header-data-entry">
            <span class="invoice-entry-title">Nr Faktury: </span>
            <span class="invoice-entry">{invoice_number}</span>
        </div>
        """

        issue_date_container = f"""
        <div class="invoice-header-data-entry">
            <span class="invoice-entry-title">Data wystawienia: </span>
            <span class="invoice-entry">{issue_date}</span>
        </div>
        """

        sale_date_container = f"""
        <div class="invoice-header-data-entry">
            <span class="invoice-entry-title">Data sprzedaży: </span>
            <span class="invoice-entry">{sale_date}</span>
        </div>
        """

        payment_method_container = f"""
        <div class="invoice-header-data-entry">
            <span class="invoice-entry-title">Metoda Płatności: </span>
            <span class="invoice-entry">{payment_method}</span>
        </div>
        """

        payment_deadline_container = f"""
        <div class="invoice-header-data-entry">
            <span class="invoice-entry-title">Termin Płatności: </span>
            <span class="invoice-entry">{payment_deadline}</span>
        </div>
        """

        buyer_data_container = f"""
        <div class="invoice-client-data">
            <span class="invoice-client-entry-title">Nabywca</span>
            <span class="invoice-client-entry">{external_business_entity.company_name}</span>
            <span class="invoice-client-entry">{external_business_entity.street}; {external_business_entity.postal_code} {external_business_entity.city}</span>
            <span class="invoice-client-entry">NIP {external_business_entity.nip}</span>
        </div>
        """
        invoice_items_container = ""
        for invoice_item in invoice_items:
            vat_percent = ((invoice_item.gross_value - invoice_item.net_value) / invoice_item.net_value) * 100
            gross_sum += invoice_item.gross_value
            item = f"""
            <tr>
                <td>{invoice_item.ordinal_number}</th>
                <td>{invoice_item.item_description}</th>
                <td>{invoice_item.number_of_items}</th>
                <td>{invoice_item.net_value} PLN</th>
                <td>{vat_percent} %</th>
                <td>{invoice_item.gross_value} PLN</th>
            </tr>
            """
            invoice_items_container += item 

        gross_sum_container = f"""
        <div class="invoice-products-payment">
            <span class="invoice-products-payment-title">Do zapłaty razem:</span>
            <span class="invoice-products-payment-amount">{gross_sum} PLN</span>
        </div>
        """

        notes_container = f"""
        <div class="invoice-details">
            <span class="invoice-details-title">Uwagi:</span>
            <span class="invoice-details-text">{notes}</span>
        </div>
        """

        html_invoice = f"""
        <html>
            {styles}
            <body>
                <div class="invoice-main">
                    <div class="invoice-header">
                        <div class="invoice-title">
                            <span class="invoice-header-title">Faktura</span>
                            {seller_data_container}
                        </div>
                        <hr />
                        <div class="invoice-header-data">
                            <div>
                                {invoice_number_container}
                                {issue_date_container}
                                {sale_date_container}
                            </div>
                            <div>
                                {payment_method_container}
                                {payment_deadline_container}
                            </div>
                        </div>
                    </div>
                    {buyer_data_container}
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
                                {invoice_items_container}
                            </tbody>
                        </table>
                        {gross_sum_container}
                        {notes_container}
                        <div class="invoice-sign-wrapper">
                            <span class="invoice-sign">Osoba upoważniona do odbioru</span>
                            <span class="invoice-sign">Osoba upoważniona do wystawienia</span>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """

        return html_invoice
    except Exception as e:
        logger.error(f"invoice_generator() Error: {e}")