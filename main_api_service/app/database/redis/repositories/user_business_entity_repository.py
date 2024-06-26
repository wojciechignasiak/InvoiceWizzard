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
from app.database.redis.repositories.user_business_entity_repository_abc import UserBusinessEntityRedisRepositoryABC
import json
import datetime

class UserBusinessEntityRedisRepository(BaseRedisRepository, UserBusinessEntityRedisRepositoryABC):

    async def initialize_user_business_entity_removal(self, key_id: str, user_business_entity_id: str) -> bool:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_user_business_entity_removal_initialized: bool = await self.redis_client.set(
                name=f"remove_user_business_entity:{key_id}", 
                value=json.dumps({"id":f"{user_business_entity_id}"}),
                ex=expiry_time)
            if is_user_business_entity_removal_initialized is False:
                raise RedisSetError("Error durning initializing user business entity removal.")
            return is_user_business_entity_removal_initialized
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserBusinessEntitiesRedisRepository.initialize_user_business_entity_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
    
    async def retrieve_user_business_entity_removal(self, key_id: str) -> bytes:
        try:
            user_business_entity_to_remove: bytes = await self.redis_client.get(f"remove_user_business_entity:{key_id}")
            if user_business_entity_to_remove is None:
                raise RedisNotFoundError("Not found user business entity to remove in database.")
            return user_business_entity_to_remove
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserBusinessEntitiesRedisRepository.retrieve_user_business_entity_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")

    async def delete_user_business_entity_removal(self, key_id: str):
        try:
            await self.redis_client.delete(f"remove_user_business_entity:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserBusinessEntitiesRedisRepository.delete_user_business_entity_removal() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")