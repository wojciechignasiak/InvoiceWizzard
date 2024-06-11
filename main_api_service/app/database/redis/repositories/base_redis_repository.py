from fastapi import Depends
from redis.asyncio import Redis
from app.database.redis.client.get_redis_client import get_redis_client

class BaseRedisRepository:
    __slots__ = 'redis_client'
    
    def __init__(self, redis_client: Redis = Depends(get_redis_client)):
        self.redis_client: Redis = redis_client