from app.database.redis.repositories.base_redis_repository import BaseRedisRepository
from app.database.redis.repositories.invoice_repository_abc import InvoiceRedisRepositoryABC
from app.logging import logger
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisNotFoundError,
    RedisSetError,
)
from redis.exceptions import (
    RedisError, 
    ConnectionError, 
    TimeoutError, 
    ResponseError
)
import json


class InvoiceRedisRepository(BaseRedisRepository, InvoiceRedisRepositoryABC):

    async def initialize_invoice_removal(self, key_id: str, invoice_id: str) -> bool:
        try:
            is_invoice_removal_initialized = self.redis_client.setex(f"remove_invoice:{key_id}", 60*60*48, json.dumps({"id":f"{invoice_id}"}))
            if is_invoice_removal_initialized == False:
                raise RedisSetError("Error durning initializing invoice removal.")
            return is_invoice_removal_initialized
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"InvoiceRedisRepository.initialize_invoice_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")

    async def retrieve_invoice_removal(self, key_id: str) -> bytes:
        try:
            invoice_to_remove = self.redis_client.get(f"remove_invoice:{key_id}")
            if invoice_to_remove == None:
                raise RedisNotFoundError("Not found invoice to remove in database.")
            return invoice_to_remove
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"InvoiceRedisRepository.retrieve_invoice_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")

    async def delete_invoice_removal(self, key_id: str) -> bool:
        try:
            self.redis_client.delete(f"remove_invoice:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"InvoiceRedisRepository.delete_invoice_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")