from abc import ABC, abstractmethod

class ResponseExtractionUtilityABC(ABC):

    @abstractmethod
    def extract_json_string(self, invoice_data: str) -> str:
        ...
    @abstractmethod
    def convert_json_string_to_json(self, json_str: str) -> str:
        ...