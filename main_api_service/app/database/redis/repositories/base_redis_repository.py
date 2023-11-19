from redis import Redis

class BaseRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client: Redis = redis_client