#internal modules
from app.models.invoice_model import InvoiceModel
from main_api_service.app.logging import logger

#3rd party modules
from PIL import Image
from weasyprint import HTML
import imageio
import img2pdf

#1st party modules
from io import BytesIO
import os
import shutil
from pathlib import Path
import asyncio
from typing import Protocol
from uuid import UUID

class IIOStorage(Protocol):

    async def remove_invoice_file(self, user_id: UUID, invoice_id: UUID) -> None:
        ...

    async def add_invoice_file(self, user_id: UUID, invoice_id: UUID, invoice_file: bytes) -> None:
        ...

    async def get_invoice_file(self, user_id: UUID, invoice_id: UUID) -> Path | None:
        ...


class IOStorage():
    
    async def remove_invoice_folder(user_id: str, invoice_id: str, folder: str):
        try:
            await asyncio.to_thread(shutil.rmtree(f"/usr/app/invoice-files/{folder}/{user_id}/{invoice_id}"))
        except Exception as e:
            logger.error(f"FilesRepository.remove_invoice_folder() Error: {e}")
            raise Exception("Error durning removing file occured.")
        
    async def remove_ai_extraction_failure_folder(file_path: str):
        try:
            await asyncio.to_thread(shutil.rmtree(os.path.dirname(file_path)))
        except Exception as e:
            logger.error(f"FilesRepository.remove_ai_extraction_failure_folder() Error: {e}")
            raise Exception("Error durning removing file occured.")

    async def save_invoice_file(file_path: str, file_data: bytes):
        try:
            await asyncio.to_thread(os.makedirs, os.path.dirname(file_path), True)
            await asyncio.to_thread(lambda: Path(file_path).write_bytes(file_data))
        except Exception as e:
            logger.error(f"FilesRepository.save_invoice_file() Error: {e}")
            raise Exception("Error during saving file occurred.")

    async def convert_from_img_to_pdf_and_save_invoice_file(file_path: str, file_extension: str, file_data: bytes):
        try:
            await asyncio.to_thread(os.makedirs, os.path.dirname(file_path), True)
            
            def process_image():
                with imageio.get_reader(BytesIO(file_data)) as reader:
                    is_it_mpo: bool = len(reader) > 1

                    if is_it_mpo:
                        base_image = Image.fromarray(reader.get_data(0))
                        with BytesIO() as jpeg_stream:
                            base_image.save(jpeg_stream, format=file_extension)
                            return jpeg_stream.getvalue()
                return file_data
            
            processed_data = await asyncio.to_thread(process_image)
            pdf_data = await asyncio.to_thread(img2pdf.convert, processed_data)
            await asyncio.to_thread(lambda: Path(file_path).write_bytes(pdf_data))
        except Exception as e:
            logger.error(f"FilesRepository.convert_from_img_to_pdf_and_save_invoice_file() Error: {e}")
            raise Exception("Error during converting img to pdf file occurred.")

    async def get_invoice_pdf_file(file_path: str) -> Path:
        try:
            return Path(file_path)
        except Exception as e:
            logger.error(f"FilesRepository.get_invoice_pdf_file() Error: {e}")
            raise Exception("Error during getting file occurred.")
    
    async def invoice_html_to_pdf(invoice_html: str, file_path: str):
        try:
            directory = os.path.dirname(file_path)
            await asyncio.to_thread(os.makedirs, directory, True)
            
            def generate_pdf():
                return HTML(string=invoice_html).write_pdf()
            
            pdf_document = await asyncio.to_thread(generate_pdf)
            if pdf_document:
                await asyncio.to_thread(lambda: Path(file_path).write_bytes(pdf_document))
        except Exception as e:
            logger.error(f"FilesRepository.invoice_html_to_pdf() Error: {e}")
            raise Exception("Error during converting HTML to PDF occurred.")

    async def copy_ai_invoice_to_invoice_folder(ai_invoice_id: str, user_id: str, invoice_id: str):
        try:
            await asyncio.to_thread(shutil.copyfile,
                f"/usr/app/invoice-files/ai-invoice/{user_id}/{ai_invoice_id}.pdf",
                f"/usr/app/invoice-files/invoice/{user_id}/{invoice_id}.pdf")
        except Exception as e:
            logger.error(f"FilesRepository.copy_ai_invoice_to_invoice_folder() Error: {e}")
            raise Exception("Error during copying file occurred.")
