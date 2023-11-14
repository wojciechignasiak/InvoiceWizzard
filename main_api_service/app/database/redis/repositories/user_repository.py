from redis import Redis
from app.models.user_model import NewUserTemporaryModel, ConfirmUserEmailChange, ConfirmUserPasswordChange
from app.models.jwt_model import JWTPayloadModel
from redis.exceptions import RedisError
import datetime
from uuid import uuid4
import json

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
        
    async def save_jwt(self, jwt_token: str, jwt_payload: JWTPayloadModel) -> bool:
        try:
            exp_time = jwt_payload.exp - datetime.datetime.utcnow()
            result = self.redis_client.setex(f"JWT:{jwt_token}:{jwt_payload.id}", exp_time, jwt_payload.model_dump_json())
            return result
        except RedisError as e:
            print("UserRedisRepository.save_jwt() Error: ", e)
            raise RedisError(f"Error durning saving jwt to database occured")
    
    async def retrieve_jwt(self, jwt_token: str) -> bytes|None:
        try:
            key: list = self.redis_client.keys(f"JWT:{jwt_token}:*")
            if key:
                result = self.redis_client.get(key[0])
            else:
                return None
            if result:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.retrieve_jwt() Error: ", e)
            raise RedisError(f"Error durning retrieving jwt from database occured")
        
    async def delete_all_jwt_of_user(self, user_id: str):
        try:
            key: list = self.redis_client.keys(f"JWT:*:{user_id}")
            if key:
                for item in key:
                    self.redis_client.delete(item)
        except RedisError as e:
            print("UserRedisRepository.delete_all_jwt_of_user() Error: ", e)
            raise RedisError(f"Error durning deleting jwts from database occured")
        
    async def save_new_email(self, new_email: ConfirmUserEmailChange) -> str|None:
        try:
            id = uuid4()
            result = self.redis_client.setex(f"new_email:{id}", 60*60*48, new_email.model_dump_json())
            if result == True:
                return str(id)
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.save_new_email() Error: ", e)
            raise RedisError(f"Error durning saving new email to database occured")
        
    async def retrieve_new_email(self, id: str) -> bytes|None:
        try:
            result = self.redis_client.get(f"new_email:{id}")
            if result:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.retrieve_new_email() Error: ", e)
            raise RedisError(f"Error durning retrieving new_email from database occured")
        
    async def delete_new_email(self, id):
        try:
            result = self.redis_client.delete(f"new_email:{id}")
            if result:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.delete_new_email() Error: ", e)
            raise RedisError(f"Error durning retrieving new_email from database occured")
        
    async def save_new_password(self, new_password: ConfirmUserPasswordChange) -> str|None:
        try:
            id = uuid4()
            result = self.redis_client.setex(f"new_password:{id}", 60*60*48, new_password.model_dump_json())
            if result == True:
                return str(id)
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.save_new_password() Error: ", e)
            raise RedisError(f"Error durning saving new password to database occured")
        
    async def retrieve_new_password(self, id: str) -> bytes|None:
        try:
            result = self.redis_client.get(f"new_password:{id}")
            if result:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.retrieve_new_password() Error: ", e)
            raise RedisError(f"Error durning retrieving new_password from database occured")
        
    async def delete_new_password(self, id):
        try:
            result = self.redis_client.delete(f"new_password:{id}")
            if result:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.delete_new_password() Error: ", e)
            raise RedisError(f"Error durning retrieving new_password from database occured")
        
    async def save_reset_password(self, new_password: ConfirmUserPasswordChange) -> str|None:
        try:
            id = uuid4()
            result = self.redis_client.setex(f"reset_password:{id}", 60*60*48, new_password.model_dump_json())
            if result == True:
                return str(id)
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.save_reset_password() Error: ", e)
            raise RedisError(f"Error durning saving reset password to database occured")
        
    async def retrieve_reset_password(self, id: str) -> bytes|None:
        try:
            result = self.redis_client.get(f"reset_password:{id}")
            if result:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.retrieve_reset_password() Error: ", e)
            raise RedisError(f"Error durning retrieving reset_password from database occured")
        
    async def delete_reset_password(self, id):
        try:
            result = self.redis_client.delete(f"reset_password:{id}")
            if result:
                return result
            else:
                return None
        except RedisError as e:
            print("UserRedisRepository.delete_reset_password() Error: ", e)
            raise RedisError(f"Error durning retrieving reset_password from database occured")