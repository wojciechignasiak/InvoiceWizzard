from app.database.redis.repositories.base_redis_repository import BaseRedisRepository
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
from app.database.redis.repositories.external_business_entity_repository_abc import ExternalBusinessEntityRedisRepositoryABC
import json
import datetime

class ExternalBusinessEntityRedisRepository(BaseRedisRepository, ExternalBusinessEntityRedisRepositoryABC):

    async def initialize_external_business_entity_removal(self, key_id: str, external_business_entity_id: str) -> bool:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_external_business_entity_removal_initialized: bool = await self.redis_client.set(
                name=f"remove_external_business_entity:{key_id}", 
                value=json.dumps({"id":f"{external_business_entity_id}"}),
                ex=expiry_time)
            if is_external_business_entity_removal_initialized is False:
                raise RedisSetError("Error durning initializing external business entity removal.")
            return is_external_business_entity_removal_initialized
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"ExternalBusinessEntitiesRedisRepository.initialize_external_business_entity_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
    
    async def retrieve_external_business_entity_removal(self, key_id: str) -> bytes:
        try:
            external_business_entity_to_remove: bytes = await self.redis_client.get(f"remove_external_business_entity:{key_id}")
            if external_business_entity_to_remove is None:
                raise RedisNotFoundError("Not found external business entity to remove in database.")
            return external_business_entity_to_remove
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"ExternalBusinessEntitiesRedisRepository.retrieve_external_business_entity_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")

    async def delete_external_business_entity_removal(self, key_id: str):
        try:
            await self.redis_client.delete(f"remove_external_business_entity:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"ExternalBusinessEntitiesRedisRepository.delete_external_business_entity_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")