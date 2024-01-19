from typing import List

def get_invoice_extraction_prompt(nip_list: List[str]):

    instructions = """
            You are an extractor of information from embedded invoices. Your task is to identify and extract information about the invoice that may be present in the provided text.

            Invoice data in embedded files may be in Polish or English language.

            invoice_number may be named like "invoice no", "nr faktury", "faktura numer", "invoice number" or similar.

            Invoice numbers can be in different formats, e.g. "1/2021", "2/2021", "3/2021", etc., by period, e.g. "1/03/2021", "2/03/2021" (March invoices), "1/04/2021" (April invoices), etc., contractors, e.g. "1/A/2021", "2/A/2021", "1/B/2021" (for contractors A and B), employees "1/AN/2021", "2/AN/2021", "1/JK/2021" (issued by Anna Nowak and Jan Kowalski). Numbering methods can also be combined into different forms , e.g. "5/04/AN/2021" (the fifth invoice issued in April by Anna Nowak).

            issue_date may be named "data wystawienia", "issue date" or similar.

            sale_date may be named "data sprzedazy", "sale date", "sprzedano dnia" or similar.

            payment_method may be named "metoda płatności", "forma płatności", "payment method" or simillar.

            notes may be named "uwagi", "Uwagi:" "notatki", "uwagi do zamowienia", "uwagi do faktury", "notes" or simillar.

            is_settled should be {True} or {False}.

            is_settled is True when seller in field named "sprzedawca", "seller" or simmilar "nip" is one from user business nip from provided list.

            if you find issue, sale date and payment_deadline provide it in format YYYY-MM-DD

            If there is no searched information just place {None} value in provided template.

            You can identify which business entity belongs to user by nip value."""
    
    user_nip_list = f"User business entities nip list {nip_list}"

    json_part ="""
            Your response should contain the following information without any additional words or details:
            AI answer:
            {
            "invoice_number": "{invoice_number}",
            "issue_date": "{issue_date}",
            "sale_date": "{sale_date}",
            "payment_method": "{payment_method}",
            "payment_deadline": "{payment_deadline}",
            "notes": "{notes}",
            "is_settled": "{is_settled}",
            }
            AI answer end
            Please use the provided format to respond do not add any additional information.
            """
    
    return str(instructions + user_nip_list + json_part)