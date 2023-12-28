from app.files.files_repository_abc import FilesRepositoryABC
import shutil
import os
import img2pdf
import os
from PIL import Image
import imageio
import io

class FilesRepository(FilesRepositoryABC):
    
    async def remove_invoice_folder(self, user_id: str, invoice_id: str):
        shutil.rmtree(f"/usr/app/invoice/{user_id}/{invoice_id}")

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