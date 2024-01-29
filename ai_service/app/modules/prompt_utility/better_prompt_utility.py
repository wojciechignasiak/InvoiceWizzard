from typing import List
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate

class BetterPromptUtility:

    def __init__(self):
        pass
    
    def single_prompt(self, nip_list: List):

        examples = [
            {
                "user_business_entity_nip_list_and_embeddings": "[1166042492, 9651914734]" "some embedded document",
                "answer": """{{
                                "invoice": {{
                                    "invoice_number": "1/2023"
                                    "issue_date": 2023-10-01,
                                    "sale_date": 2023-10-01,
                                    "payment_method": "Card",
                                    "payment_deadline": 2023-10-15,
                                    "notes": None, 
                                    "is_issued": True
                                }}
                                "user_business_entity": 
                                {{
                                    "company_name": "Wielka Firma Sp. z o.o.",
                                    "city": "Warszawa",
                                    "postal_code": 00-001,
                                    "street": "ul. Nowa 21/37",
                                    "nip": "1166042492"
                                }}
                                "external_business_entity": 
                                {{
                                    "name": "Wojciech Ignasiak", 
                                    "city": Bełchatów,
                                    "postal_code": 97-400,
                                    "street": "ul. Paderewskiego 6/13",
                                    "nip": None
                                }}
                            }}"""
            },
            {
                "user_business_entity_nip_list_and_embeddings": "[1166042492, 9651914734]" "some embedded document",
                "answer": """{{
                                "invoice": {{
                                    "invoice_number": "5/2023"
                                    "issue_date": 2023-12-01,
                                    "sale_date": 2023-12-01,
                                    "payment_method": "Card",
                                    "payment_deadline": 2023-12-15,
                                    "notes": "Prosze dokladnie zapakowac produkty", 
                                    "is_issued": False
                                }}
                                "user_business_entity": 
                                {{
                                    "company_name": "Wielka Firma Sp. z o.o.",
                                    "city": "Warszawa",
                                    "postal_code": 00-001,
                                    "street": "ul. Nowa 21/37",
                                    "nip": "1266042493"
                                }}
                                "external_business_entity": 
                                {{
                                    "name": "Inna Wielka Firma Sp. z o.o.", 
                                    "city": Bełchatów,
                                    "postal_code": 97-400,
                                    "street": "ul. Paderewskiego 6/13",
                                    "nip": "9651914734"
                                }}
                            }}"""
            },
            {
                "user_business_entity_nip_list_and_embeddings": "[1166042492, 9651914734]" "some embedded document",
                "answer": """{{
                                "invoice": {{
                                    "invoice_number": "10/A/2023"
                                    "issue_date": 2023-08-01,
                                    "sale_date": 2023-08-01,
                                    "payment_method": "Przelew",
                                    "payment_deadline": 2023-08-15,
                                    "notes": None, 
                                    "is_issued": False
                                }}
                                "user_business_entity": 
                                {{
                                    "company_name": "Wielka Firma Sp. z o.o.",
                                    "city": "Warszawa",
                                    "postal_code": 00-001,
                                    "street": "ul. Nowa 21/37",
                                    "nip": "1266042493"
                                }}
                                "external_business_entity": 
                                {{
                                    "name": "Inna Wielka Firma Sp. z o.o.", 
                                    "city": Bełchatów,
                                    "postal_code": 97-400,
                                    "street": "ul. Paderewskiego 6/13",
                                    "nip": "9158934734"
                                }}
                            }}"""
            }
        ] 

        example_template = """
        Input: {user_business_entity_nip_list}
        AI: {answer}
        """

        example_prompt = PromptTemplate(
            input_variables=["user_business_entity_nip_list", "answer"],
            template=example_template
        )

        prefix = """
        Extract searched data from embedded invoice in the correct JSON format.
        is_issued is True only if seller nip is provided on nip numbers list.
        external business entity name can be first name and last name of physical person like "Jan Kowalski" or "John Smith". It can also be company name
        If you find nip number in invoice with marks that are not digits like ./-? etc. remove them. nip number should contian only digits
        """

        suffix = """
        Input: {user_business_entity_nip_list}
        AI:
        """

        few_shot_prompt_template = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix,
            suffix=suffix,
            input_variables=["user_business_entity_nip_list"],
            example_separator="\n\n"
        )

        prompt = few_shot_prompt_template.format(user_business_entity_nip_list=nip_list)

        return prompt
    
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
