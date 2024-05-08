from abc import ABC, abstractmethod


class OCRUtilityABC(ABC):

    @abstractmethod
    def convert_pdf_to_images(self, pdf_path) -> list:
        pass

    @abstractmethod
    def extract_text_from_image(self, image) -> str:
        pass

    @abstractmethod
    def extract_text_from_pdf(self, pdf_path) -> list:
        pass


