from abc import ABC, abstractmethod


class FilesRepositoryABC(ABC):
    
    @abstractmethod
    async def remove_invoice_folder(self, user_id: str, invoice_id: str, folder: str):
        ...

    @abstractmethod
    async def save_invoice_file(self, file_path: str, file_data: bytes):
        ...

    @abstractmethod
    async def convert_from_img_to_pdf_and_save_invoice_file(self, file_path: str, file_extension: str, file_data: bytes):
        ...

    @abstractmethod
    async def get_invoice_pdf_file(self, file_path: str):
        ...
    
    @abstractmethod
    async def invoice_html_to_pdf(invoice_html: str, file_path: str):
        ...