from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores.redis import Redis
from langchain.chains import RetrievalQA
from langchain.llms.ollama import Ollama
from abc import ABC, abstractmethod


class OllamaUtilityABC(ABC):
    
    @abstractmethod
    def generate_embedding_model(self) -> OllamaEmbeddings:
        ...

    @abstractmethod
    def generate_model(self) -> Ollama:
        ...

    @abstractmethod
    def generate_qa_chain(self, redis: Redis, ollama_model: Ollama) -> RetrievalQA:
        ...