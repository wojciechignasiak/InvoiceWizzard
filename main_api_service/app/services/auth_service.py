#internal modules
from main_api_service.app.database.redis.repositories.user_repository import IUserRedisRepository, new_user_redis_repository
from main_api_service.app.models.jwt_model import (
    JWTDataModel, 
    JWTPayloadModel
    )
from main_api_service.app.custom_exceptions.custom_exceptions import (
    AuthError,
    ServiceError,
    DatabaseError,
    LogicError
    )

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends, status
import argon2
import jwt

#1st party libraries
from typing import Protocol
import os
import re
import datetime
from uuid import UUID


class IAuthService(Protocol):
        
    async def get_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        ...

    async def delete_jwt(self, token: str) -> None:
        ...

    async def delete_all_jwts(self, user_id: UUID) -> None:
        ...

    @staticmethod
    def salt_generator() -> str:
        ...

    @staticmethod
    def hash_password(salt: str, password: str) -> str:
        ...

    @staticmethod
    def verify_password(salt: str, password: str, password_hash: str) -> None:
        ...

    @staticmethod
    def jwt_encoder(jwt_data: JWTDataModel) -> str:
        ...

    @staticmethod
    def validate_password(password: str, repeated_password: str) -> bool:
        ...

    @staticmethod
    def validate_email_address(email_address: str, repeated_email_address: str) -> bool:
        ...

    async def create_and_save_jwt_token(self, user_id: UUID, email_address: str, jwt_expiration_time: datetime.datetime, salt: str) -> str:
        ...

def new_auth_service(
    user_redis_repository: IUserRedisRepository = Depends(new_user_redis_repository)
) -> IAuthService:
    try:
        return AuthService(
            user_redis_repository
        )
    except Exception as e:
        raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while converting jwt payload to jwt payload model",
                argument={'token': 'anonymized'},
                child_error=e,
            )

class AuthService(IAuthService):

    __slots__ = ('user_redis_repository',)

    def __init__(
            self,
            user_redis_repository: IUserRedisRepository
            ):
        self._user_redis_repository: IUserRedisRepository = user_redis_repository

    async def get_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        try:
            jwt_payload: bytes | None = await self._user_redis_repository.get_jwt_token(token.credentials)
            if not jwt_payload:
                raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, message="Unauthorized access or token expired")
            return await self._convert_jwt_payload_to_jwt_payload_model(jwt_payload)
        except AuthError as e:
            raise e
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'token': token},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while getting JWT token from database",
                argument={'token': token},
                child_error=e,
            )
    async def delete_jwt(self, token: str) -> None:
        try:
            await self._user_redis_repository.delete_jwt_token(token)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while converting jwt payload to jwt payload model",
                argument={'token': 'anonymized'},
                child_error=e,
            )
    
    async def delete_all_jwts(self, user_id: UUID) -> None:
        try:
            await self._user_redis_repository.delete_all_jwt_tokens_of_user(user_id)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while converting jwt payload to jwt payload model",
                argument={'token': 'anonymized'},
                child_error=e,
            )

    @staticmethod
    def _convert_jwt_payload_to_jwt_payload_model(jwt_payload: bytes) -> JWTPayloadModel:
        try:
            return JWTPayloadModel.model_validate_json(jwt_payload)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while converting jwt payload to jwt payload model",
                argument={'jwt_payload': 'anonymized'},
                child_error=e,
            )

    @staticmethod
    def salt_generator() -> str:
        try:
            return str(os.urandom(16))
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while generating salt",
                argument=None,
                child_error=e,
            )

    @staticmethod
    def hash_password(salt: str, password: str) -> str:
        try:
            ph = argon2.PasswordHasher()
            hashed_password = ph.hash(password + salt)
            return hashed_password
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while hashing password",
                argument={'salt': 'anonymized', 'password': 'anonymized'},
                child_error=e,
            )

    @staticmethod
    def verify_password(salt: str, password: str, password_hash: str) -> None:
        try:
            ph = argon2.PasswordHasher()
            is_the_same: bool = ph.verify(password_hash, password+salt)
            if not is_the_same:
                raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, message="Password not correct")
        except AuthError as e:
            raise AuthError(
                status_code=e.status_code,
                message=e.args[0],
                argument={'salt': 'anonymized', 'password': 'anonymized', 'password_hash': 'anonymized'}
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while converting jwt payload to jwt payload model",
                argument={'salt': 'anonymized', 'password': 'anonymized', 'password_hash': 'anonymized'},
                child_error=e,
            )

    @staticmethod
    def jwt_encoder(jwt_data: JWTDataModel) -> str:
        try:
            jwt_token = jwt.encode(
                jwt_data.payload.model_dump(),
                jwt_data.secret,
                jwt_data.algorithm
            )
            return jwt_token
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while converting jwt payload to jwt payload model",
                argument={'jwt_data': jwt_data},
                child_error=e,
            )

    @staticmethod
    def validate_password(password: str, repeated_password: str) -> bool:
        try:
            if password != repeated_password:
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided passwords are not the same")
            if len(password) < 8:
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided password is too short")
            if not re.search(r'[A-Z]', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contain at least 1 capital letter")
            if not re.search(r'[a-z]', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contain at least 1 lowercase letter")
            if not re.search(r'\d', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contain at least 1 digit")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contain at least 1 special character")
            return True
        except LogicError as e:
            raise LogicError(
                status_code=e.args[0],
                message=e.message,
                argument={'password': 'anonymized', 'repeated_password': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while checking does password meets conditions",
                argument={'password': 'anonymized', 'repeated_password': 'anonymized'},
                child_error=e,
            )

    @staticmethod
    def validate_email_address(email_address: str, repeated_email_address: str) -> bool:
        try:
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, email_address):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided email is in wrong format")
            if email_address != repeated_email_address:
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided email addresses don't match")
            return True
        except LogicError as e:
            raise LogicError(
                status_code=e.args[0],
                message=e.message,
                argument={'email_address': email_address, 'repeated_email_address': repeated_email_address},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while checking if email has a valid format",
                argument={'email_address': email_address, 'repeated_email_address': repeated_email_address},
                child_error=e,
            )

    async def create_and_save_jwt_token(self, user_id: UUID, email_address: str, jwt_expiration_time: datetime.datetime, salt: str) -> str:
        try:
            jwt_payload: JWTPayloadModel = JWTPayloadModel(
                user_id=user_id,
                email=email_address, 
                exp=jwt_expiration_time
                )
            jwt_data: JWTDataModel = JWTDataModel(
                secret=salt, 
                payload=jwt_payload
                )
            jwt_token: str = self.jwt_encoder(jwt_data)
            await self._user_redis_repository.save_jwt_token(jwt_token, jwt_payload)
            return jwt_token
        except ServiceError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.args[0],
                argument={'user_id': user_id, 'email_address': email_address, 'jwt_expiration_time': jwt_expiration_time, 'salt': 'anonymized'},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while checking if email has a valid format",
                argument={'user_id': user_id, 'email_address': email_address, 'jwt_expiration_time': jwt_expiration_time, 'salt': 'anonymized'},
                child_error=e,
            )
