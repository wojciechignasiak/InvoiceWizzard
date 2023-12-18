from weasyprint import HTML
from app.logging import logger
import os

async def invoice_html_to_pdf(invoice_html: str, file_path: str) -> None:
    try:
        directory = os.path.dirname(file_path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        pdf_document = HTML(string=invoice_html).write_pdf()

        if len(pdf_document) > 0:
            with open(file_path, 'wb') as f:
                f.write(pdf_document)
    except Exception as e:
        logger.error(f"invoice_html_to_pdf() Error: {e}")