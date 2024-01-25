from modules.pdf_utility.pdf_utility import PdfUtility
from modules.ollama_utility.ollama_utility import OllamaUtility
from modules.redisearch_repository.redisearch_repository import RedisearchRepository
from langchain.vectorstores.redis import Redis
from langchain.chains import RetrievalQA
from typing import List, Dict
from modules.logging.logging import logger
from uuid import uuid4
import json
from modules.prompt_utility.prompt_utility import PromptUtility
from modules.kafka_utilities.kafka_producer import KafkaProducer


class ExtractData:
    
    def __init__(self) -> None:
        self.ollama_utility = OllamaUtility()
        self.pdf_utility = PdfUtility()
        self.prompt_utility = PromptUtility()
        self.redis_repository = RedisearchRepository()
        self.text_embedding_model = self.ollama_utility.generate_embedding_model()
        self.text_extraction_model = self.ollama_utility.generate_model()
        self.kafka_producer = KafkaProducer()

    async def is_scan_or_text(self, message) -> Dict:
        try:
            is_scan = self.pdf_utility.is_scan(
                filepath=message["file_location"]
                )
            
            if is_scan is True:
                await self.kafka_producer.is_scanned(message)
            else:
                result = self.extract_data_from_text(message)
                await self.kafka_producer.extracted_invoice_data(result)
        except Exception as e:
            logger.error(f"ExtractData.is_scan_or_text() Error: {e}")

    def extract_data_from_text(self, message: str):
        try:
            print("Creating redis index...")
            redis_index: str = f"pdf_index_{uuid4()}"
            print(f"Created redis index: {redis_index}")

            print("Chunking pdf file...")
            chunked_pdf: List = self.pdf_utility.chunk_pdf_file(message["file_location"])
            print("PDF chunked!")

            print("Embedding pdf file...")
            redis: Redis = self.redis_repository.embedding_file(
                pdf_pages=chunked_pdf,
                ollama_embedding_model=self.text_embedding_model,
                redis_index=redis_index)
            
            print("Embedding pdf file done!")

            invoice_and_business_entities_prompt = self.prompt_utility.get_invoice_and_business_entities_extraction_prompt(message["user_business_entities_nip"])
            invoice_items_prompt = self.prompt_utility.get_invoice_items_extraction_prompt()

            print("Generating QA chain...")
            qa_chain: RetrievalQA = self.ollama_utility.generate_qa_chain(
                redis=redis,
                ollama_model=self.text_extraction_model)
            print("QA chain generated!")

            print("Asking question...")
            result: Dict = qa_chain.invoke({"query": invoice_and_business_entities_prompt})
            print("Question asked!")
            invoice_and_business_entities: str = result["result"]
            
            invoice_and_business_entities_json_data = json.loads(invoice_and_business_entities)

            #Invoice items
            print("Asking question...")
            result: Dict = qa_chain.invoke({"query": invoice_items_prompt})
            print("Question asked!")
            invoice_items_data = result["result"]

            invoice_items_json_data = json.loads(invoice_items_data)

            print("Extracting responses...")
            invoice_and_business_entities_json_data["invoice"]["invoice_pdf"] = message["file_location"]
            invoice_and_business_entities_json_data["user_id"] = message["file_location"].split('/')[5]
            invoice_and_business_entities_json_data["invoice_items"] = invoice_items_json_data["invoice_items"]

            print("Extracting responses done!")

            print("Cleaning redis index...")
            self.redis_repository.clean_data_from_index(redis_index, redis)
            print("Cleaning redis index done!")
        except Exception as e:
            logger.error(f"ExtractData.extract_data_from_text() Error: {e}")