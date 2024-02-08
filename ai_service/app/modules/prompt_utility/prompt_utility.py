from typing import List, Dict, Literal

class PromptUtility:

    def __init__(self):
        pass
    
    def get_invoice_and_business_entities_extraction_prompt(self, nip_list: List):
        info = f"""
        User business NIP numbers: {nip_list}
        'is_issued' is true only if the seller's NIP is provided on the NIP numbers list.
        External business entity name can be the first name and last name of a physical person like "Jan Kowalski" or "John Smith". It can also be a company name.
        If you find a NIP number in the invoice with marks that are not digits like ./-? etc., remove these marks. The NIP number should contain only digits.
        Extract data from the invoice in the correct JSON format:
        """

        searched_data ="""
        START:
        {
            "invoice": {
                "invoice_number": str,  # It have a format like "1/2023", "1/01/2023", "1/A/2023", "1/CD/2023", "1/CD/02/2023" or just numbers etc.
                "issue_date": "date yyyy-mm-dd",
                "sale_date": "date yyyy-mm-dd",
                "payment_method": str,
                "payment_deadline": "date yyyy-mm-dd",
                "notes": str,  # It can be mentioned as "Remarks", "Notes", "Uwagi", "Uwagi do faktury", etc.
                "is_issued": bool  # true when the seller's NIP is on the provided NIP list; false when the buyer's NIP or no NIP is found in the embedded invoice.
            },
            "user_business_entity": {
                "company_name": str,
                "city": str,
                "postal_code": str,
                "street": str,
                "nip": str 
            },
            "external_business_entity": { 
                "name": str, 
                "city": str,
                "postal_code": str,
                "street": str,
                "nip": str 
            }
        }
        STOP
        If any information is missing, represent it with a null value. Ensure that each JSON corresponds to a distinct item or service, and adhere strictly to the provided format. Respond only in the specified format.
        """

        return str(info + searched_data)

    def get_invoice_items_extraction_prompt(self) -> str:
        info = f"""
                Generate separate JSON structures for invoice items based on the provided embeddings. Each JSON structure should follow the format below:
                """
        searched_data ="""
                START:
                {
                invoice_items: [
                    {
                    "item_description": str, # It is name of product or service
                    "number_of_items": int, # quantity of sold product or service with that name
                    "net_value": float, # It is net value of single type of product or service
                    "gross_value": float # It is gross value of single typer of product or service 
                    }
                    # If there is more items add , and place next json in the list
                ]
                }
                STOP
                If any information is missing, represent it with null value. Ensure that each JSON corresponds to a distinct item or service, and adhere strictly to the provided format. Respond only in the specified format.
                """
        
        return str(info + searched_data)
    

    def get_invoice_and_business_entities_extraction_from_text_prompt(self, nip_list: List, extracted_text: List):
        info = f"""
        User business NIP numbers: {nip_list}
        'is_issued' is true only if the seller's NIP is provided on the NIP numbers list.
        External business entity name can be the first name and last name of a physical person like "Jan Kowalski" or "John Smith". It can also be a company name.
        If you find a NIP number in the invoice with marks that are not digits like ./-? etc., remove these marks. The NIP number should contain only digits.
        Extract data from the invoice in the correct JSON format:
        """

        searched_data ="""
        START:
        {
            "invoice": {
                "invoice_number": str,  # It have a format like "1/2023", "1/01/2023", "1/A/2023", "1/CD/2023", "1/CD/02/2023" or just numbers etc.
                "issue_date": "date yyyy-mm-dd",
                "sale_date": "date yyyy-mm-dd",
                "payment_method": str,
                "payment_deadline": "date yyyy-mm-dd",
                "notes": str,  # It can be mentioned as "Remarks", "Notes", "Uwagi", "Uwagi do faktury", etc.
                "is_issued": bool  # true when the seller's NIP is on the provided NIP list; false when the buyer's NIP or no NIP is found in the embedded invoice.
            },
            "user_business_entity": {
                "company_name": str,
                "city": str,
                "postal_code": str,
                "street": str,
                "nip": str 
            },
            "external_business_entity": { 
                "name": str, 
                "city": str,
                "postal_code": str,
                "street": str,
                "nip": str 
            }
        }
        STOP
        If any information is missing, represent it with a null value. Ensure that each JSON corresponds to a distinct item or service, and adhere strictly to the provided format. Respond only in the specified format.
        """

        data = f"""
            Text to extract from:
            {extracted_text}
        """

        return str(info + searched_data + data)

    def get_invoice_items_extraction_from_text_prompt(self, extracted_text: List) -> str:

        info ="""
                Generate separate JSON structures for invoice items based on the provided embeddings. Each JSON structure should follow the format below:
                START:
                {
                invoice_items: [
                    {
                    "item_description": str, # It is name of product or service
                    "number_of_items": int, # quantity of sold product or service with that name
                    "net_value": float, # It is net value of single type of product or service
                    "gross_value": float # It is gross value of single typer of product or service 
                    }
                    # If there is more items add , and place next json in the list
                ]
                }
                STOP
                If any information is missing, represent it with null value. Ensure that each JSON corresponds to a distinct item or service, and adhere strictly to the provided format. Respond only in the specified format.

                """
        searched_data = f"""
                Text to extract from:
                {extracted_text}
                """
        
        return str(info + searched_data)
    
    def get_correct_json_invoice_items_prompt(self, extracted_invoice_item: str) -> Literal:
        info = """
            Context: You will be getting JSON's. Some of them may be incorrect. If provided JSON is incorrect fix it and return in correct format. If provided JSON is correct return it without changing anything.

            Example:
            Input: 
            {
                invoice_items: [
                    {
                    "item_description": "Piłka",
                    "number_of_items": 1, # quantity of sold product or service with that name
                    "net_value": 10.0, # It is net value of single type of product or service
                    "gross_value": 12.0 # It is gross value of single typer of product or service 
                    }
                    
                ]
                }
            Output:
            {
                invoice_items: [
                    {
                    "item_description": "Piłka",
                    "number_of_items": 1,
                    "net_value": 10.0,
                    "gross_value": 12.0
                    }
                    
                ]
                }
            
            """
        searched_data = f"""
                Input: {extracted_invoice_item}
                Answer:
                """
        
        return str(info + searched_data)
    
    def get_correct_json_invoice_and_business_entities_prompt(self, extracted_invoice_and_business_data: str) -> Literal:
        info = """
            Context: You will be getting JSON's. Some of them may be incorrect. If provided JSON is incorrect fix it and return in correct format. If provided JSON is correct return it without changing anything.

            Example:
            Input: 
            {
                "invoice": {
                    "invoice_number": "1/2023",
                    "issue_date": 2024-01-01:12,
                    "sale_date": 2024-01-01,
                    "payment_method": "Card",
                    "payment_deadline": 2024-01-04,
                    "notes": "It's invoice note",
                    "is_issued": True  # true when the seller's NIP is on the provided NIP list; false when the buyer's NIP or no NIP is found in the embedded invoice.
                },
                "user_business_entity": {
                    "company_name": "Company name",
                    "city": "Warsaw",
                    "postal_code": "98-404",
                    "street": "ul. Nowa 1/2",
                    "nip": "123-456-789"
                },
                "external_business_entity": { 
                    "name": "Company name 2", 
                    "city": "Bełchatów",
                    "postal_code": 97-400,
                    "street": "Okrzei 3/4",
                    "nip": 
                }
            }
            Output:
            {
                "invoice": {
                    "invoice_number": "1/2023",
                    "issue_date": 2024-01-01,
                    "sale_date": 2024-01-01,
                    "payment_method": "Card",
                    "payment_deadline": 2024-01-04,
                    "notes": "It's invoice note",  
                    "is_issued": True
                },
                "user_business_entity": {
                    "company_name": "Company name",
                    "city": "Warsaw",
                    "postal_code": "98-404",
                    "street": "ul. Nowa 1/2",
                    "nip": "123456789"
                },
                "external_business_entity": { 
                    "name": "Company name 2", 
                    "city": "Bełchatów",
                    "postal_code": 97-400,
                    "street": "Okrzei 3/4",
                    "nip": null
                }
            }
            """
        searched_data = f"""
                Input: {extracted_invoice_and_business_data}
                Answer:
                """
        
        return str(info+searched_data)
