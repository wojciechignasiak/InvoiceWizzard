from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores.redis import Redis
from langchain.chains import RetrievalQA, create_extraction_chain
from langchain.llms.ollama import Ollama
from modules.logging.logging import logger
import os
from typing import Dict



class OllamaUtility:

    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST")
        self.port = os.getenv("OLLAMA_PORT")
        
    def generate_embedding_model(self):
        try:
            embedding_model: OllamaEmbeddings = OllamaEmbeddings(model="openchat", base_url=f"http://{self.host}:{self.port}")

            return embedding_model
        except Exception as e:
            logger.error(f"OllamaUtility.generate_embedding_model() Error: {e}")
            raise Exception(f"OllamaUtility.generate_embedding_model() Error: {e}")

    def generate_model(self):
        try:
            model: Ollama  = Ollama(model="openchat", base_url=f"http://{self.host}:{self.port}", temperature=0)
            return model
        except Exception as e:
            logger.error(f"OllamaUtility.generate_model() Error: {e}")
            raise Exception(f"OllamaUtility.generate_model() Error: {e}")

    def generate_qa_chain(self, redis: Redis, ollama_model: Ollama):
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=ollama_model, 
                retriever=redis.as_retriever(search_kwargs={'k': 2})
                )
            return qa_chain
        except Exception as e:
            logger.error(f"OllamaUtility.generate_qa_chain() Error: {e}")
            raise Exception(f"OllamaUtility.generate_qa_chain() Error: {e}")
        
    def generate_extraction_chain(self, schema: Dict, ollama_model: Ollama):
        try:
            extraction_chain = create_extraction_chain(
                schema=schema,
                llm=ollama_model,
            )
            return extraction_chain
        except Exception as e:
            logger.error(f"OllamaUtility.generate_extraction_chain() Error: {e}")
            raise Exception(f"OllamaUtility.generate_extraction_chain() Error: {e}")