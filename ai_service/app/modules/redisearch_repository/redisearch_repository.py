import os
from langchain.vectorstores.redis import Redis
from langchain_community.embeddings.ollama import OllamaEmbeddings
from modules.logging.logging import logger

class RedisearchRepository:
    
    def __init__(self) -> None:
        self.host = os.getenv("REDISEARCH_HOST")
        self.port = os.getenv("REDISEARCH_PORT")

    def embedding_file(self, pdf_pages: list, ollama_embedding_model: OllamaEmbeddings, redis_index: str) -> Redis:
        try:
            redis: Redis = Redis.from_documents(
                documents=pdf_pages, 
                embedding=ollama_embedding_model, 
                redis_url=f"redis://{self.host}:{self.port}",
                index_name=redis_index
            )
            return redis
        except Exception as e:
            logger.error(f"RedisearchRepository.embedding_file() Error: {e}")
            raise Exception(f"RedisearchRepository.embedding_file() Error: {e}")

    def clean_data_from_index(self, index_name: str, redis: Redis):
        try:
            redis.drop_index(index_name, delete_documents=True, redis_url=f"redis://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"RedisearchRepository.clean_data_from_index() Error: {e}")
            raise Exception(f"RedisearchRepository.clean_data_from_index() Error: {e}")