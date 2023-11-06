from redis import Redis
from main_api_service.app.models.account_registration_model import AccountRegistrationTemporaryDataModel
from redis.exceptions import RedisError
from uuid import uuid4


class AccountRegistrationRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client: Redis = redis_client
        
    async def create(self, account_data: AccountRegistrationTemporaryDataModel) -> str:
        try:
            id = f"ART:{uuid4()}"
            result = self.redis_client.setex(id, 60*60*24*14, account_data.model_dump_json())
            if result == True:
                return id
            else:
                raise RedisError("Error durning saving account")
        except RedisError as e:
            print(e)
            raise RedisError(f"Error durning saving account to database occured")
        
    