from app.files.files_repository_abc import FilesRepositoryABC
from app.logging import logger
from pathlib import Path
from PIL import Image
from weasyprint import HTML
import shutil
import imageio
import img2pdf
import os
import io

class FilesRepository(FilesRepositoryABC):
    
    async def remove_invoice_folder(self, user_id: str, invoice_id: str, folder: str):
        try:
            shutil.rmtree(f"/usr/app/invoice-files/{folder}/{user_id}/{invoice_id}")
        except Exception as e:
            logger.error(f"FilesRepository.remove_invoice_folder() Error: {e}")
            raise Exception("Error durning removing file occured.")

    async def save_invoice_file(self, file_path: str, file_data: bytes):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file_data)
        except Exception as e:
            logger.error(f"FilesRepository.save_invoice_file() Error: {e}")
            raise Exception("Error durning removing file occured.")

    async def convert_from_img_to_pdf_and_save_invoice_file(self, file_path: str, file_extension: str, file_data: bytes):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
            with imageio.get_reader(io.BytesIO(file_data)) as reader:
                is_it_mpo: bool = len(reader) > 1

                if is_it_mpo:
                    base_image = Image.fromarray(reader.get_data(0))

                    with io.BytesIO() as jpeg_stream:
                        base_image.save(jpeg_stream, format=file_extension)
                        file_data = jpeg_stream.getvalue()

            with open(file_path, "wb") as f:
                f.write(img2pdf.convert(file_data))
        except Exception as e:
            logger.error(f"FilesRepository.convert_from_img_to_pdf_and_save_invoice_file() Error: {e}")
            raise Exception("Error durning converting img to pdf file occured.")

    async def get_invoice_pdf_file(self, file_path: str):
        try:
            return Path(file_path)
        except Exception as e:
            logger.error(f"FilesRepository.get_invoice_pdf_file() Error: {e}")
            raise Exception("Error durning getting file occured.")
    
    
    async def invoice_html_to_pdf(invoice_html: str, file_path: str):
        try:
            directory = os.path.dirname(file_path)
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            pdf_document = HTML(string=invoice_html).write_pdf()

            if len(pdf_document) > 0:
                with open(file_path, 'wb') as f:
                    f.write(pdf_document)
        except Exception as e:
            logger.error(f"FilesRepository.invoice_html_to_pdf() Error: {e}")
            raise Exception("Error durning converting html to pdf file occured.")

    async def copy_ai_invoice_to_invoice_folder(ai_invoice_id: str, user_id: str, invoice_id: str):
        try:
            shutil.copyfile(
                src=f"/usr/app/invoice-files/ai-invoice/{user_id}/{ai_invoice_id}.pdf",
                dst=f"/usr/app/invoice-files/invoice/{user_id}/{invoice_id}.pdf")
        except Exception as e:
            logger.error(f"FilesRepository.copy_ai_invoice_to_invoice_folder() Error: {e}")
            raise Exception("Error durning coping file occured.")