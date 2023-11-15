from redis import Redis
from app.models.user_model import (CreateUserModel, ConfirmUserEmailChange, ConfirmUserPasswordChange)
from app.models.jwt_model import JWTPayloadModel
from redis.exceptions import RedisError, ConnectionError, TimeoutError, ResponseError
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisNotFoundError,
    RedisSetError
)
import datetime
from uuid import uuid4
import logging

class UserRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client: Redis = redis_client
        
    async def create_user(self, key_id: str, new_user: CreateUserModel) -> bool:
        try:
            is_user_created = self.redis_client.setex(f"user:{key_id}:{str(new_user.email)}", 60*60*24*14, new_user.model_dump_json())
            if is_user_created == False:
                raise RedisSetError("Cannot register new user in database.")
            return is_user_created
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.create_user() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        except Exception as e:
            logging.exception(f"UserRedisRepository.create_user() Error: {e}")
            raise RedisDatabaseError("Unexpected error related to database occurred.")
        
    async def search_user_by_id(self, key_id: str) -> bytes:
        try:
            key: list = self.redis_client.keys(f"user:{key_id}:*")
            if key:
                user: bytes = self.redis_client.get(key[0])
            else:
                raise RedisNotFoundError("User with provided id not found in database.")
            return user
        except RedisNotFoundError as e:
            logging.exception(f"UserRedisRepository.search_user_by_id() Error: {e}")
            raise RedisNotFoundError(e)
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.search_user_by_id() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        except Exception as e:
            logging.exception(f"UserRedisRepository.search_user_by_id() Error: {e}")
            raise RedisDatabaseError("Unexpected error related to database occurred.")
    
    async def is_user_arleady_registered(self, email_address: str) -> bool:
        try:
            key: list = self.redis_client.keys(f"user:*:{email_address}")
            if key:
                return True
            else:
                return False
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.is_user_arleady_registered() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_user_by_id(self, key_id: str) -> bool:
        try:
            key: list = self.redis_client.keys(f"user:{key_id}:*")

            if key:
                self.redis_client.delete(key[0])
                return True
            else:
                return False
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            print("UserRedisRepository.delete_user_by_id() Error: ", e)
            raise RedisDatabaseError("Error durning deleting temporary account from database occured.")
        
    async def save_jwt(self, jwt_token: str, jwt_payload: JWTPayloadModel) -> bool:
        try:
            exp_time = jwt_payload.exp - datetime.datetime.utcnow()
            is_jwt_saved = self.redis_client.setex(f"JWT:{jwt_token}:{jwt_payload.id}", exp_time, jwt_payload.model_dump_json())
            if is_jwt_saved == False:
                raise RedisSetError("Error occured durning saving JWT token to database.")
            return is_jwt_saved
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.save_jwt() Error: {e}")
            raise RedisDatabaseError("Error durning saving jwt to database occured.")
    
    async def retrieve_jwt(self, jwt_token: str) -> bytes:
        try:
            key: list = self.redis_client.keys(f"JWT:{jwt_token}:*")
            if key:
                result = self.redis_client.get(key[0])
                return result
            else:
                raise RedisNotFoundError("JWT token not found in database.")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.retrieve_jwt() Error: {e}")
            raise RedisDatabaseError("Error durning retrieving jwt token from database occured.")
        
    async def delete_all_jwt_tokens_of_user(self, user_id: str):
        try:
            key: list = self.redis_client.keys(f"JWT:*:{user_id}")
            if key:
                for item in key:
                    self.redis_client.delete(item)
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.delete_all_jwt_of_user() Error: {e}")
            raise RedisDatabaseError("Error durning deleting jwts from database occured.")
        
    async def save_new_email(self, key_id: str, new_email: ConfirmUserEmailChange) -> bool:
        try:
            result = self.redis_client.setex(f"new_email:{key_id}", 60*60*48, new_email.model_dump_json())
            if result == False:
                raise RedisSetError("Error durning saving new email to database occured")
            return result
                
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.save_new_email() Error: {e}")
            raise RedisDatabaseError("Error durning saving new email to database occured.")
        
    async def retrieve_new_email(self, key_id: str) -> bytes:
        try:
            result = self.redis_client.get(f"new_email:{key_id}")
            if result == None:
                raise RedisNotFoundError("New email not found in database.")
            return result
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.retrieve_new_email() Error: {e}")
            raise RedisDatabaseError("Error durning retrieving new_email from database occured.")
        
    async def delete_new_email(self, key_id):
        try:
            self.redis_client.delete(f"new_email:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logging.exception(f"UserRedisRepository.delete_new_email() Error: {e}")
            raise RedisDatabaseError("Error durning retrieving new_email from database occured.")
        
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