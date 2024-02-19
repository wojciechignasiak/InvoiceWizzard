from abc import ABC, abstractmethod
from langchain.vectorstores.redis import Redis
from langchain_community.embeddings.ollama import OllamaEmbeddings

class RedisearchRepositoryABC(ABC):

    @abstractmethod
    def embedding_file(self, pdf_pages: list, ollama_embedding_model: OllamaEmbeddings, redis_index: str) -> Redis:
        ...

    @abstractmethod
    def clean_data_from_index(self, index_name: str, redis: Redis):
        ...