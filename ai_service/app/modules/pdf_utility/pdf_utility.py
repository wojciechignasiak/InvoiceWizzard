from langchain.document_loaders.pdf import PyPDFLoader
from typing import List
from PyPDF2 import PdfReader


class PdfUtility:

    def chunk_pdf_file(self, file_location: str) -> List:
        try:
            loader: PyPDFLoader = PyPDFLoader(file_location)
            pdf_pages: List = loader.load_and_split()
            return pdf_pages
        except Exception as e:
            print({"chunk_pdf_file": f"Error: {e}"})

    def is_scan(self, filepath: str) -> bool:
        try:
            pdf = PdfReader(filepath)
            page = pdf.pages[0]
            text = page.extract_text()

            if text.strip() == "":
                return True
            else:
                return False
        except Exception as e:
            print(f"is_scan error: Failed to process PDF. {str(e)}")