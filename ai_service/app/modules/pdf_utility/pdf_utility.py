from langchain.document_loaders.pdf import PyPDFLoader
from typing import List
from PyPDF2 import PdfReader
from modules.logging.logging import logger

class PdfUtility:

    def chunk_pdf_file(self, file_location: str) -> List:
        try:
            loader: PyPDFLoader = PyPDFLoader(file_location)
            pdf_pages: List = loader.load_and_split()
            return pdf_pages
        except Exception as e:
            logger.error(f"PdfUtility.chunk_pdf_file() Error: {e}")

    def is_scan(self, file_location: str) -> bool:
        try:
            pdf = PdfReader(file_location)
            page = pdf.pages[0]
            text = page.extract_text()

            if text.strip() == "":
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"PdfUtility.is_scan() Error: {e}")