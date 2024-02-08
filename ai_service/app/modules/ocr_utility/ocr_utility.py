import fitz  
from PIL import Image
import pytesseract
import io
from modules.logging.logging import logger

class OCRUtility:

    def __init__(self) -> None:
        pass

    def convert_pdf_to_images(self, pdf_path):
        try:
            images = []
            pdf_document = fitz.open(pdf_path)
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    base_image = pdf_document.extract_image(img[0])
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    images.append(image)
            return images
        except Exception as e:
            logger.error(f"OCRUtility.convert_pdf_to_images() Error: {e}")
            raise Exception(f"OCRUtility.convert_pdf_to_images() Error: {e}")

    def extract_text_from_image(self, image):
        try:
            return pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"OCRUtility.extract_text_from_image() Error: {e}")
            raise Exception(f"OCRUtility.extract_text_from_image() Error: {e}")

    def extract_text_from_pdf(self, pdf_path):
        try:
            images = self.convert_pdf_to_images(pdf_path)
            extracted_text = []
            for image in images:
                text = self.extract_text_from_image(image)
                extracted_text.append(text)
            return extracted_text
        except Exception as e:
            logger.error(f"OCRUtility.extract_text_from_pdf() Error: {e}")
            raise Exception(f"OCRUtility.extract_text_from_pdf() Error: {e}")
