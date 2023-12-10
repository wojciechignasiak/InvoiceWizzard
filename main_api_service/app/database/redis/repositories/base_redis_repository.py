from redis import Redis

class BaseRedisRepository:
    __slots__ = 'redis_client'
    
    def __init__(self, redis_client: Redis):
        self.redis_client: Redis = redis_client