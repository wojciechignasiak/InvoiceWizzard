from abc import ABC, abstractmethod

class PromptUtilityABC(ABC):
    
    @abstractmethod
    def get_invoice_and_business_entities_extraction_prompt(self, nip_list: list) -> str:
        ...

    @abstractmethod
    def get_invoice_items_extraction_prompt(self) -> str:
        ...

    @abstractmethod
    def get_invoice_and_business_entities_extraction_from_text_prompt(self, nip_list: list, extracted_text: list) -> str:
        ...

    @abstractmethod
    def get_invoice_items_extraction_from_text_prompt(self, extracted_text: list) -> str:
        ...
    
    @abstractmethod
    def get_correct_json_invoice_items_prompt(self, extracted_invoice_item: str) -> str:
        ...
    
    @abstractmethod
    def get_correct_json_invoice_and_business_entities_prompt(self, extracted_invoice_and_business_data: str) -> str:
        ...
