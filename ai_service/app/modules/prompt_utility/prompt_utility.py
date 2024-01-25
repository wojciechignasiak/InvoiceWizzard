from typing import List

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
                "invoice_number": str,  # It can be referred to as "Invoice number", "Invoice no", "nr faktury", "Numer faktury", "NR Faktury", etc., and will have a format like "1/2023", "1/01/2023", "1/A/2023", "1/CD/2023", "1/CD/02/2023", etc.
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
