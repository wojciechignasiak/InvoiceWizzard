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
from typing import List


class UserRedisRepository(BaseRedisRepository, UserRedisRepositoryABC):

    async def create_user(self, key_id: str, new_user: CreateUserModel) -> bool:
        try:
            expiry_time = datetime.timedelta(days=14)
            is_user_created: bool = await self.redis_client.set(
                name=f"user:{key_id}:{str(new_user.email)}",
                value=new_user.model_dump_json(),
                ex=expiry_time
            )
            if is_user_created is False:
                raise RedisSetError("Cannot register new user in database.")
            return is_user_created
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.create_user() Error: {e}")
            raise RedisDatabaseError("Error related to the database occurred.")

        
    async def search_user_by_id(self, key_id: str) -> bytes:
        try:
            user_key: List = await self.redis_client.keys(f"user:{key_id}:*")
            if user_key:
                user: bytes = await self.redis_client.get(user_key[0])
            else:
                raise RedisNotFoundError("User with provided id not found in database.")
            return user
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.search_user_by_id() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
    
    async def is_user_arleady_registered(self, email_address: str) -> bool:
        try:
            user_key: List = await self.redis_client.keys(f"user:*:{email_address}")
            if user_key:
                return True
            else:
                return False
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.is_user_arleady_registered() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_user_by_id(self, key_id: str) -> bool:
        try:
            user_key: List = await self.redis_client.keys(f"user:{key_id}:*")

            if user_key:
                await self.redis_client.delete(user_key[0])
                return True
            else:
                return False
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_user_by_id() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def save_jwt(self, jwt_token: str, jwt_payload: JWTPayloadModel) -> bool:
        try:
            expiry_time = jwt_payload.exp - datetime.datetime.utcnow()
            is_jwt_saved: bool = await self.redis_client.set(
                name=f"JWT:{jwt_token}:{jwt_payload.id}",
                value=jwt_payload.model_dump_json(),
                ex=expiry_time)
            if is_jwt_saved is False:
                raise RedisSetError("Error occured durning saving JWT token to database.")
            return is_jwt_saved
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.save_jwt() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
    
    async def retrieve_jwt(self, jwt_token: str) -> bytes:
        try:
            jwt_token_key: List = await self.redis_client.keys(f"JWT:{jwt_token}:*")
            if jwt_token_key:
                result = await self.redis_client.get(jwt_token_key[0])
                return result
            else:
                raise RedisJWTNotFoundError("Unauthorized access or JWT token expired.")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.retrieve_jwt() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_all_jwt_tokens_of_user(self, user_id: str):
        try:
            jwt_token_keys: List = await self.redis_client.keys(f"JWT:*:{user_id}")
            if jwt_token_keys:
                for token_key in jwt_token_keys:
                    await self.redis_client.delete(token_key)
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_all_jwt_of_user() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_jwt_token(self, user_id: str, token: str):
        try:
            await self.redis_client.delete(f"JWT:{token}:{user_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_jwt_token() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def save_new_email(self, key_id: str, new_email: ConfirmedUserEmailChangeModel) -> bool:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_new_email_saved: bool = await self.redis_client.set(
                name=f"new_email:{key_id}", 
                value=new_email.model_dump_json(),
                ex=expiry_time)
            if is_new_email_saved is False:
                raise RedisSetError("Error durning saving new email to database occured")
            return is_new_email_saved
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.save_new_email() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def retrieve_new_email(self, key_id: str) -> bytes:
        try:
            new_email: bytes = await self.redis_client.get(f"new_email:{key_id}")
            if new_email is None:
                raise RedisNotFoundError("New email not found in database.")
            return new_email
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.retrieve_new_email() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def delete_new_email(self, key_id):
        try:
            await self.redis_client.delete(f"new_email:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_new_email() Error: {e}")
            raise RedisDatabaseError("Error related to database occurred.")
        
    async def save_new_password(self, key_id: str, new_password: ConfirmedUserPasswordChangeModel) -> bool:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_new_password_saved: bool = await self.redis_client.set(
                name=f"new_password:{key_id}", 
                value=new_password.model_dump_json(),
                ex=expiry_time)
            if is_new_password_saved is False:
                raise RedisSetError("Error durning saving new password to database occured.")
            return is_new_password_saved
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.save_new_password() Error: {e}")
            raise RedisDatabaseError("Error durning saving new password to database occured.")
        
    async def retrieve_new_password(self, key_id: str) -> bytes:
        try:
            new_password: bytes = await self.redis_client.get(f"new_password:{key_id}")
            if new_password is None:
                raise RedisNotFoundError("New password not found in database.")
            return new_password
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.retrieve_new_password() Error: {e}")
            raise RedisDatabaseError("Error durning retrieving new password from database occured.")
        
    async def delete_new_password(self, key_id: str):
        try:
            await self.redis_client.delete(f"new_password:{key_id}")
        except (RedisError, ResponseError, ConnectionError, TimeoutError) as e:
            logger.error(f"UserRedisRepository.delete_new_password() Error: {e}")
            raise RedisDatabaseError("Error durning deleting new password from database occured.")