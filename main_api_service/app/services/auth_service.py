import os
import base64
import argon2
from argon2 import PasswordHasher
import jwt
from app.models.jwt_model import JWTDataModel
from app.logging import logger
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.factories.get_repositories_factory import get_repositories_factory
from app.factories.repositories_factory_abc import RepositoriesFactoryABC
from app.database.redis.repositories.user_repository_abc import UserRedisRepositoryABC
from app.models.jwt_model import JWTPayloadModel
from app.database.redis.exceptions.custom_redis_exceptions import RedisJWTNotFoundError, RedisDatabaseError

class AuthService:

    def __init__(self, repositories_factory: RepositoriesFactoryABC = Depends(get_repositories_factory)):
        self.__repositories_factory: RepositoriesFactoryABC = repositories_factory
    
    async def get_user_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        try:
            user_redis_repository: UserRedisRepositoryABC = await self.__repositories_factory.return_user_redis_repository()

            jwt_payload: bytes = await user_redis_repository.retrieve_jwt(token.credentials)

            jwt_payload: JWTPayloadModel = JWTPayloadModel.model_validate_json(jwt_payload)

            return jwt_payload
        except (RedisJWTNotFoundError, RedisDatabaseError)  as e:
            logger.error(f"AuthService.get_user_jwt() Error: {e}")
            raise e
    
    async def __salt_generator(self) -> str:
        try:
            salt: bytes = os.urandom(16)
            return base64.b64encode(salt).decode('utf-8')
        except Exception as e:
            logger.error(f"AuthService.salt_generator() Error: {e}")
            raise Exception("Error durning salt generation occured.")

    async def hash_password(self, password: str) -> str:
        try:
            ph = argon2.PasswordHasher()
            hashed_password = ph.hash(password + await self.__salt_generator())
            return hashed_password
        except Exception as e:
            logger.error(f"AuthService.hash_password() Error: {e}")
            raise Exception("Error durning hashing password occured.")
    
    async def verify_password(self, salt: str, password: str, hash: str) -> bool:
        try:
            password_hasher: PasswordHasher = PasswordHasher()
            is_the_same = password_hasher.verify(hash, password+salt)
            return is_the_same
        except Exception as e:
            logger.error(f"AuthService.verify_password() Error: {e}")
            raise Exception("Error durning verifying password.")

    async def jwt_encoder(self, jwt_data: JWTDataModel) -> str:
        try:
            jwt_token = jwt.encode(
                jwt_data.payload.model_dump(),
                jwt_data.secret,
                jwt_data.algorithm
            )
            return jwt_token
        except Exception as e:
            logger.error(f"AuthService.jwt_encoder() Error: {e}")
            raise Exception("Error durning encoding jwt occured.")
    
    