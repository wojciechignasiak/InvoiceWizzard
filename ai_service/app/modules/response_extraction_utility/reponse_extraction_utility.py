from modules.logging.logging import logger
import json

class ResponseExtractionUtility:

    def __init__(self):
        pass

    def extract_json_string(self, invoice_data: str) -> str:
        try:
            start_pos = invoice_data.find('{')
            end_pos = invoice_data.rfind('}')
            if start_pos != -1 and end_pos != -1:
                json_str = invoice_data[start_pos:end_pos+1]
                return json_str
            else:
                return None
        except Exception as e:
            logger.error(f"ResponseExtractionUtility.extract_json_string() Error: {e}")

    def convert_json_string_to_json(self, json_str: str) -> str:
        try:
            return json.load(json_str)
        except Exception as e:
            logger.error(f"ResponseExtractionUtility.convert_json_string_to_json() Error: {e}")
