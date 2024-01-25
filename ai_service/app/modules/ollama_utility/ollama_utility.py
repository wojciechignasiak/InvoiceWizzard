from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores.redis import Redis
from langchain.chains import RetrievalQA
from langchain.llms.ollama import Ollama
from modules.logging.logging import logger
import os



class OllamaUtility:

    def __init__(self) -> None:
        self.host = os.getenv("OLLAMA_HOST")
        self.port = os.getenv("OLLAMA_PORT")
        
    def generate_embedding_model(self):
        try:
            embedding_model: OllamaEmbeddings = OllamaEmbeddings(base_url=f"http://{self.host}:{self.port}")

            return embedding_model
        except Exception as e:
            logger.error(f"OllamaUtility.generate_embedding_model() Error: {e}")

    def generate_model(self):
        try:
            model: Ollama  = Ollama(model="openchat", base_url=f"http://{self.host}:{self.port}", temperature=0)
            return model
        except Exception as e:
            logger.error(f"OllamaUtility.generate_model() Error: {e}")

    def generate_qa_chain(self, redis: Redis, ollama_model: Ollama):
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=ollama_model, 
                retriever=redis.as_retriever(search_kwargs={'k': 2})
                )
            return qa_chain
        except Exception as e:
            logger.error(f"OllamaUtility.generate_qa_chain() Error: {e}")