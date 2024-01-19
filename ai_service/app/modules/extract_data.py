from modules.pdf_utility.pdf_utility import PdfUtility
from modules.ollama_utility.ollama_utility import OllamaUtility
from modules.redisearch_repository.redisearch_repository import RedisearchRepository
from langchain.chains import RetrievalQA
from typing import List, Dict
from uuid import uuid4
import os
from modules.prompts.get_invoice_extraction_prompt import get_invoice_extraction_prompt
from modules.json_parser import json_parser

async def extract_data(message):

    
    print("Data extraction started!")
    ollama_utility = OllamaUtility()
    pdf_utility = PdfUtility()
    
    redis_repository = RedisearchRepository()

    print("Creating redis index...")
    redis_index: str = f"pdf_index_{uuid4()}"
    print(f"Created redis index: {redis_index}")

    print("Chunking pdf file...")
    chunked_pdf: List = pdf_utility.chunk_pdf_file(message["file_location"])
    print("PDF chunked!")

    print("Embedding pdf file...")
    redis = redis_repository.embedding_file(
        pdf_pages=chunked_pdf,
        ollama_embedding_model=ollama_utility.generate_embedding_model(),
        redis_index=redis_index)
    print("Embedding pdf file done!")

    prompt: str = get_invoice_extraction_prompt(message["user_business_entities_nip"])

    print("Generating QA chain...")
    qa_chain: RetrievalQA = ollama_utility.generate_qa_chain(
        redis=redis,
        ollama_model=ollama_utility.generate_llama2())
    print("QA chain generated!")

    

    print("Asking question...")
    result: Dict = qa_chain.invoke({"query": prompt})
    print("Question asked!")
    print("Result:")
    print(result["result"])
    print(type(result))
    print("Parsing result...")
    extracted_json = json_parser(
        json_string=str(result["result"])
    )
    print("Result parsed!")

    print("Extracted json:")
    print(extracted_json)

    print("Cleaning redis index...")
    redis_repository.clean_data_from_index(redis_index, redis)
    print("Cleaning redis index done!")

