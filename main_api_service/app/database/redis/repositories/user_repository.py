import datetime
from app.database.redis.repositories.base_redis_repository import BaseRedisRepository
from app.models.user_model import (
    CreateUserModel, 
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )
from app.logging import logger
from app.database.redis.exceptions.custom_redis_exceptions import (
    RedisDatabaseError,
    RedisNotFoundError,
    RedisSetError,
    RedisJWTNotFoundError
)
from app.models.jwt_model import JWTPayloadModel
from redis.exceptions import (
    RedisError, 
    ConnectionError, 
    TimeoutError, 
    ResponseError
)
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC


class UserRedisRepository(BaseRedisRepository, UserRedisRepositoryABC):

    async def create_user(self, key_id: str, new_user: CreateUserModel) -> bool:
        try:
            is_user_created = self.redis_client.setex(f"user:{key_id}:{str(new_user.email)}", 
                                                    60*60*24*14, 
                                                    new_user.model_dump_json()
                                                    )
            if is_user_created == False:
                raise RedisSetError("Cannot register new user in database.")
            return is_user_created
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.create_user() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def search_user_by_id(self, key_id: str) -> bytes:
        try:
            user_key: list = self.redis_client.keys(f"user:{key_id}:*")
            if user_key:
                user: bytes = self.redis_client.get(user_key[0])
            else:
                raise RedisNotFoundError("User with provided id not found in database.")
            return user
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.search_user_by_id() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
    
    async def is_user_arleady_registered(self, email_address: str) -> bool:
        try:
            user_key: list = self.redis_client.keys(f"user:*:{email_address}")
            if user_key:
                return True
            else:
                return False
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.is_user_arleady_registered() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_user_by_id(self, key_id: str) -> bool:
        try:
            user_key: list = self.redis_client.keys(f"user:{key_id}:*")

            if user_key:
                self.redis_client.delete(user_key[0])
                return True
            else:
                return False
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_user_by_id() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def save_jwt(self, jwt_token: str, jwt_payload: JWTPayloadModel) -> bool:
        try:
            exp_time = jwt_payload.exp - datetime.datetime.utcnow()
            is_jwt_saved = self.redis_client.setex(f"JWT:{jwt_token}:{jwt_payload.id}", exp_time, jwt_payload.model_dump_json())
            if is_jwt_saved == False:
                raise RedisSetError("Error occured durning saving JWT token to database.")
            return is_jwt_saved
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.save_jwt() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
    
    async def retrieve_jwt(self, jwt_token: str) -> bytes:
        try:
            jwt_token_key: list = self.redis_client.keys(f"JWT:{jwt_token}:*")
            if jwt_token_key:
                result = self.redis_client.get(jwt_token_key[0])
                return result
            else:
                raise RedisJWTNotFoundError("Unauthorized access or JWT token expired.")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.retrieve_jwt() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_all_jwt_tokens_of_user(self, user_id: str):
        try:
            jwt_token_keys: list = self.redis_client.keys(f"JWT:*:{user_id}")
            if jwt_token_keys:
                for token_key in jwt_token_keys:
                    self.redis_client.delete(token_key)
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_all_jwt_of_user() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def save_new_email(self, key_id: str, new_email: ConfirmedUserEmailChangeModel) -> bool:
        try:
            is_new_email_saved = self.redis_client.setex(f"new_email:{key_id}", 60*60*48, new_email.model_dump_json())
            if is_new_email_saved == False:
                raise RedisSetError("Error durning saving new email to database occured")
            return is_new_email_saved
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.save_new_email() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def retrieve_new_email(self, key_id: str) -> bytes:
        try:
            new_email = self.redis_client.get(f"new_email:{key_id}")
            if new_email == None:
                raise RedisNotFoundError("New email not found in database.")
            return new_email
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.retrieve_new_email() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_new_email(self, key_id):
        try:
            self.redis_client.delete(f"new_email:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_new_email() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def save_new_password(self, key_id: str, new_password: ConfirmedUserPasswordChangeModel) -> bool:
        try:
            is_new_password_saved = self.redis_client.setex(f"new_password:{key_id}", 60*60*48, new_password.model_dump_json())
            if is_new_password_saved == False:
                raise RedisSetError("Error durning saving new password to database occured.")
            return is_new_password_saved
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.save_new_password() Error: {e}")
            raise RedisDatabaseError("Error durning saving new password to database occured.")
        
    async def retrieve_new_password(self, key_id: str) -> bytes:
        try:
            new_password = self.redis_client.get(f"new_password:{key_id}")
            if new_password == None:
                raise RedisNotFoundError("New password not found in database.")
            return new_password
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.retrieve_new_password() Error: {e}")
            raise RedisDatabaseError("Error durning retrieving new password from database occured.")
        
    async def delete_new_password(self, key_id: str):
        try:
            self.redis_client.delete(f"new_password:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_new_password() Error: {e}")
            raise RedisDatabaseError("Error durning deleting new password from database occured.")