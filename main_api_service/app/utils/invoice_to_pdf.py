from weasyprint import HTML
from app.logging import logger

async def invoice_html_to_pdf(invoice_html: str, file_path: str):
    try:
        HTML(string=invoice_html).write_pdf(f'{file_path}')
    except Exception as e:
        logger.error(f"invoice_html_to_pdf() Error: {e}")