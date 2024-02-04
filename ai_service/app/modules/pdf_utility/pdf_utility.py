from io import BytesIO
from langchain.document_loaders.pdf import PyPDFLoader
from typing import List
from PyPDF2 import PdfReader
from modules.logging.logging import logger
from pdf2image import convert_from_path
import base64

class PdfUtility:

    def chunk_pdf_file(self, file_location: str) -> List:
        try:
            loader: PyPDFLoader = PyPDFLoader(file_location)
            pdf_pages: List = loader.load_and_split()
            return pdf_pages
        except Exception as e:
            logger.error(f"PdfUtility.chunk_pdf_file() Error: {e}")
            raise Exception(f"PdfUtility.chunk_pdf_file() Error: {e}")

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
            raise Exception(f"PdfUtility.is_scan() Error: {e}")
        
    def pdf_to_images_and_base64(self, pdf_path: str) -> List:
        try:
            print("Extracting base64 images form pdf...")
            images = convert_from_path(pdf_path)

            base64_images = []

            for idx, image in enumerate(images):
                img_buffer = BytesIO()
                image.save(img_buffer, format="JPEG")
                base64_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

                base64_images.append(base64_data)
            print(f"Base64 images extracted!")
            return base64_images
        except Exception as e:
            logger.error(f"PdfUtility.pdf_to_images_and_base64() Error: {e}")
            raise Exception(f"PdfUtility.pdf_to_images_and_base64() Error: {e}")