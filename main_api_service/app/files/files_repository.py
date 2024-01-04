from app.files.files_repository_abc import FilesRepositoryABC
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
        shutil.rmtree(f"/usr/app/invoice-files/{folder}/{user_id}/{invoice_id}")

    async def save_invoice_file(self, file_path: str, file_data: bytes):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_data)

    async def convert_from_img_to_pdf_and_save_invoice_file(self, file_path: str, file_extension: str, file_data: bytes):
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

    async def get_invoice_pdf_file(self, file_path: str):
        return Path(file_path)
    
    async def invoice_html_to_pdf(invoice_html: str, file_path: str):

        directory = os.path.dirname(file_path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        pdf_document = HTML(string=invoice_html).write_pdf()

        if len(pdf_document) > 0:
            with open(file_path, 'wb') as f:
                f.write(pdf_document)
