from modules.pdf_utility.pdf_utility import PdfUtility
from modules.ollama_utility.ollama_utility import OllamaUtility
from modules.redisearch_repository.redisearch_repository import RedisearchRepository
from langchain.vectorstores.redis import Redis
from langchain.chains import RetrievalQA
from typing import List, Dict
from modules.logging.logging import logger
from uuid import uuid4
from asyncio import AbstractEventLoop
import json
from modules.prompt_utility.prompt_utility import PromptUtility
from modules.kafka_utilities.kafka_producer import KafkaProducer
import asyncio
import requests
import os

class ExtractData:
    
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.ollama_utility = OllamaUtility()
        self.pdf_utility = PdfUtility()
        self.prompt_utility = PromptUtility()
        self.redis_repository = RedisearchRepository()
        self.text_embedding_model = self.ollama_utility.generate_embedding_model()
        self.text_extraction_model = self.ollama_utility.generate_model()
        self.kafka_producer = KafkaProducer(
            loop=loop,
        )
        self.__ollama_host = os.getenv("OLLAMA_HOST")
        self.__ollama_port = os.getenv("OLLAMA_PORT")

    async def is_scan_or_text(self, message) -> Dict:
        try:
            is_scan = self.pdf_utility.is_scan(
                file_location=message["file_location"]
                )
            if is_scan is True:
                self.__extract_data_from_image(message)
                await self.kafka_producer.extracted_invoice_data(result)
            else:
                result = self.__extract_data_from_text(message)
                await self.kafka_producer.extracted_invoice_data(result)
        except Exception as e:
            logger.error(f"ExtractData.is_scan_or_text() Error: {e}")

    def __extract_data_from_text(self, message: Dict):
        try:
            print("Creating redis index...")
            redis_index: str = f"pdf_index_{uuid4()}"
            print(f"Created redis index: {redis_index}")

            print("Chunking pdf file...")
            chunked_pdf: List = self.pdf_utility.chunk_pdf_file(
                file_location=message["file_location"])
            print("PDF chunked!")

            print("Embedding pdf file...")
            redis: Redis = self.redis_repository.embedding_file(
                pdf_pages=chunked_pdf,
                ollama_embedding_model=self.text_embedding_model,
                redis_index=redis_index)
            print("Embedding pdf file done!")

            print("Generating QA chain...")
            qa_chain: RetrievalQA = self.ollama_utility.generate_qa_chain(
                redis=redis,
                ollama_model=self.text_extraction_model)
            print("QA chain generated!")

            invoice_and_business_entities: str = self.__extract_invoice_and_business_entities_from_embeddings(
                message=message,
                qa_chain=qa_chain,
            )

            invoice_items_data: str = self.__extract_invoice_items_from_embeddings(
                qa_chain=qa_chain
            )

            invoice_and_business_entities: str = self.__extract_invoice_and_business_entities_json_string_from_ai_response(invoice_and_business_entities)
            invoice_items_data: str = self.__extract_invoice_items_json_string_from_ai_response(invoice_items_data)

            invoice_and_business_entities_json_data = json.loads(invoice_and_business_entities)
            invoice_items_json_data = json.loads(invoice_items_data)

            json_response = self.__generate_complete_json_response(
                message=message,
                invoice_and_business_entities_json_data=invoice_and_business_entities_json_data,
                invoice_items_json_data=invoice_items_json_data)

            return json_response
        except Exception as e:
            asyncio.create_task(self.kafka_producer.exception_occured(message))
            logger.error(f"ExtractData.__extract_data_from_text() Error: {e}")
        finally:
            self.redis_repository.clean_data_from_index(redis_index, redis)

    def __extract_data_from_image(self, message: Dict):
        try:
            base64_images: List = self.pdf_utility.pdf_to_images_and_base64(
                    pdf_path=message["file_location"]
                    )
            
            invoice_and_business_entities: str = self.__extract_invoice_and_business_entities_from_images(
                message=message,
                images=base64_images,
            )

            invoice_items_data: str = self.__extract_invoice_items_from_images(
                base64_images=base64_images,
            )

            invoice_and_business_entities: str = self.__extract_invoice_and_business_entities_json_string_from_ai_response(invoice_and_business_entities)
            invoice_items_data: str = self.__extract_invoice_items_json_string_from_ai_response(invoice_items_data)

            invoice_and_business_entities_json_data = json.loads(invoice_and_business_entities)
            invoice_items_json_data = json.loads(invoice_items_data)

            json_response = self.__generate_complete_json_response(
                message=message,
                invoice_and_business_entities_json_data=invoice_and_business_entities_json_data,
                invoice_items_json_data=invoice_items_json_data)

            return json_response
        except Exception as e:
            asyncio.create_task(self.kafka_producer.exception_occured(message))
            logger.error(f"ExtractData.__extract_data_from_image() Error: {e}")
        

    def __extract_invoice_and_business_entities_from_images(self, message: Dict, images: List) -> str:
        try:
            print("Extracting Invoice and Business entities from images...")
            invoice_and_business_entities_prompt = self.prompt_utility.get_invoice_and_business_entities_extraction_prompt(message["user_business_entities_nip"])
            body = {
                "model": "llava",
                "prompt": invoice_and_business_entities_prompt,
                "stream": False,
                "images": images,
            }
            result = requests.post(
                f"http://{self.__ollama_host}:{self.__ollama_port}/api/generate", json=body
            )
            result = result.json()
            print("Invoice and Business entities extracted!")
            return result["response"]
        except Exception as e:
            logger.error(f"ExtractData.__extract_invoice_and_business_entities_from_images() Error: {e}")
            raise Exception(f"ExtractData.__extract_invoice_and_business_entities_from_images() Error: {e}")
        
    def __extract_invoice_items_from_images(self, images: List) -> str:
        try:
            print("Extracting Invoice Items from images...")
            invoice_items_prompt = self.prompt_utility.get_invoice_items_extraction_prompt()
            body = {
                "model": "llava",
                "prompt": invoice_items_prompt,
                "stream": False,
                "images": images,
            }
            result = requests.post(
                f"http://{self.__ollama_host}:{self.__ollama_port}/api/generate", json=body
            )
            result = result.json()
            print("Invoice Items extracted!")
            return result["response"]
        except Exception as e:
            logger.error(f"ExtractData.__extract_invoice_items_from_images() Error: {e}")
            raise Exception(f"ExtractData.__extract_invoice_items_from_images() Error: {e}")
        
    def __extract_invoice_and_business_entities_from_embeddings(self, message: Dict, qa_chain: RetrievalQA) -> str:
        try:
            print("Extracting Invoice and Business entities from embeddings...")
            invoice_and_business_entities_prompt = self.prompt_utility.get_invoice_and_business_entities_extraction_prompt(message["user_business_entities_nip"])
            result: Dict = qa_chain.invoke({"query": invoice_and_business_entities_prompt})
            print("Invoice and Business entities extracted!")
            return result["result"]
        except Exception as e:
            logger.error(f"ExtractData.__extract_invoice_and_business_entities_from_embeddings() Error: {e}")
            raise Exception(f"ExtractData.__extract_invoice_and_business_entities_from_embeddings() Error: {e}")
    
    def __extract_invoice_items_from_embeddings(self, qa_chain: RetrievalQA) -> str:
        try:
            print("Extracting Invoice Items from embeddings...")
            invoice_items_prompt = self.prompt_utility.get_invoice_items_extraction_prompt()
            result: Dict = qa_chain.invoke({"query": invoice_items_prompt})
            print("Invoice Items extracted!")
            return result["result"]
        except Exception as e:
            logger.error(f"ExtractData.__extract_invoice_items_from_embeddings() Error: {e}")
            raise Exception(f"ExtractData.__extract_invoice_items_from_embeddings() Error: {e}")
    
    def __extract_invoice_and_business_entities_json_string_from_ai_response(self, ai_response: str) -> str:
        try:
            schema: Dict = self.prompt_utility.schema_for_invoice_and_business_entities()
            chain = self.ollama_utility.generate_extraction_chain(schema=schema, ollama_model=self.text_extraction_model)
            print("Extracting Invoice and Business Entities JSON string from AI response...")
            result = chain.run(ai_response)
            print("Invoice and Business Entities JSON string extracted!")
            return result["result"]
        except Exception as e:
            logger.error(f"ExtractData.__extract_invoice_and_business_entities_json_string_from_ai_response() Error: {e}")
            raise Exception(f"ExtractData.__extract_invoice_and_business_entities_json_string_from_ai_response() Error: {e}")
    
    def __extract_invoice_items_json_string_from_ai_response(self, ai_response: str) -> str:
        try:
            schema: Dict = self.prompt_utility.schema_for_invoice_items()
            chain = self.ollama_utility.generate_extraction_chain(schema=schema, ollama_model=self.text_extraction_model)
            print("Extracting Invoice Items JSON string from AI response...")
            result = chain.run(ai_response)
            print("Invoice Items JSON string extracted!")
            return result["result"]
        except Exception as e:
            logger.error(f"ExtractData.__extract_invoice_items_json_string_from_ai_response() Error: {e}")
            raise Exception(f"ExtractData.__extract_invoice_items_json_string_from_ai_response() Error: {e}")
    
    def __generate_complete_json_response(self, message, invoice_and_business_entities_json_data, invoice_items_json_data):
        try:
            print("Generating complete JSON response...")
            invoice_and_business_entities_json_data["invoice"]["invoice_pdf"] = message["file_location"]
            invoice_and_business_entities_json_data["user_id"] = message["file_location"].split('/')[5]
            invoice_and_business_entities_json_data["invoice_items"] = invoice_items_json_data["invoice_items"]
            print("Complete JSON response generated!")
            return invoice_and_business_entities_json_data
        except Exception as e:
            logger.error(f"ExtractData.__generate_complete_json_response() Error: {e}")
            raise Exception(f"ExtractData.__generate_complete_json_response() Error: {e}")

