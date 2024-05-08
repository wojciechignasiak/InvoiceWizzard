from abc import ABC, abstractmethod

class PdfUtilityABC(ABC):

    @abstractmethod
    def chunk_pdf_file(self, file_location: str) -> list:
        ...

    @abstractmethod
    def is_scan(self, file_location: str) -> bool:
        ...

    @abstractmethod
    def pdf_to_images_and_base64(self, pdf_path: str) -> list:
        ...