import json
import re

def json_parser(json_string: str) -> dict:
    try:
        json_string = re.search('AI answer:(.*)AI answer end', json_string, re.DOTALL)
        json_string = json_string.group(1)
        json_data = json.loads(json_string)
    except ValueError as e:
        print("Błąd przetwarzania JSON: ", e)
        return None
    return json_data