from redis import Redis
from app.models.user_model import NewUserTemporaryModel
from redis.exceptions import RedisError
from uuid import uuid4

class UserRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client: Redis = redis_client
        
    async def create_user(self, user: NewUserTemporaryModel) -> str|None:
        try:
            id = uuid4()
            result = self.redis_client.setex(f"user:{id}:{str(user.email)}", 60*60*24*14, user.model_dump_json())
            if result == True:
                return str(id)
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.create_user() Error: ", e)
            raise RedisError(f"Error durning saving account to database occured")
        
    async def search_user_by_id_or_email(self, value: str, search_by_email: bool = False) -> bytes|None:
        try:
            if search_by_email == False:
                key: list = self.redis_client.keys(f"user:{value}:*")
            if search_by_email == True:
                key: list = self.redis_client.keys(f"user:*:{value}")

            if key:
                result = self.redis_client.get(key[0])
            else:
                return None
            
            if result is not None:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.search_user_by_id_or_email() Error: ", e)
            raise RedisError(f"Error durning getting account from database occured")
        
    async def delete_user_by_id(self, id: str) -> int|None:
        try:
            key: list = self.redis_client.keys(f"user:{id}:*")

            if key:
                result = self.redis_client.delete(key[0])
            else:
                return None
            
            if result is not None:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.delete_user_by_id() Error: ", e)
            raise RedisError(f"Error durning deleting account from database occured")
        
    