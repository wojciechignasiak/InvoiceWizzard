#internal modules
from app.database.redis.repositories.user_repository_interface import IUserRedisRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.models.jwt_model import (
    JWTDataModel, 
    JWTPayloadModel
    )
from app.custom_exceptions.custom_exceptions import (
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


class IAuthService(Protocol):
        
    async def get_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        ...

    async def delete_jwt(self, token: str) -> None:
        ...

    async def delete_all_jwts(self, user_id: str) -> None:
        ...

    async def salt_generator() -> str:
        ...

    async def hash_password(salt: str, password: str) -> str:
        ...

    async def verify_password(salt: bytes, password: str, hash: bytes) -> bool:
        ...

    async def jwt_encoder(jwt_data: JWTDataModel) -> str:
        ...

    async def validate_password(password: str, repeated_password: str) -> bool:
        ...

    async def validate_email_address(email_address: str, reapeated_email_address: str) -> bool:
        ...

    async def create_and_save_jwt_token(self, user_id: str, email_address: str, jwt_expiration_time: datetime.datetime, salt: str) -> str:
        ...


class AuthService:

    def __init__(
            self, 
            user_redis_repository: IUserRedisRepository = Depends(UserRedisRepository)
            ):
        self._user_redis_repository: IUserRedisRepository = user_redis_repository

    async def get_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        try:
            jwt_payload: bytes | None = await self._user_redis_repository.retrieve_jwt(token.credentials)
            if not jwt_payload:
                raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, message="Unauthorized access or token expired.")
            return await self.conver_jwt_payload_to_jwt_payload_model(jwt_payload)
        except AuthError as e:
            raise e
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="AuthService.get_jwt()",
                argument={'token': token},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while getting JWT token from database.",
                class_and_method="AuthService.get_jwt()",
                argument={'token': token},
                child_error=e,
            )
    async def delete_jwt(self, token: str) -> None:
        try:
            await self._user_redis_repository.delete_jwt_token(token)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while converting jwt payload to jwt payload model.",
                class_and_method="AuthService.delete_jwt()",
                argument={'token': 'anonimized'},
                child_error=e,
            )
    
    async def delete_all_jwts(self, user_id: str) -> None:
        try:
            await self._user_redis_repository.delete_all_jwt_tokens_of_user(user_id)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while converting jwt payload to jwt payload model.",
                class_and_method="AuthService.delete_jwt()",
                argument={'token': 'anonimized'},
                child_error=e,
            )

    @staticmethod
    async def _conver_jwt_payload_to_jwt_payload_model(jwt_payload: bytes) -> JWTPayloadModel:
        try:
            return JWTPayloadModel.model_validate_json(jwt_payload)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while converting jwt payload to jwt payload model.",
                class_and_method="AuthService.conver_jwt_payload_to_jwt_payload_model()",
                argument={'jwt_payload': 'anonimized'},
                child_error=e,
            )

    @staticmethod
    async def salt_generator() -> str:
        try:
            return str(os.urandom(16))
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while generating salt.",
                class_and_method="AuthService.salt_generator()",
                argument=None,
                child_error=e,
            )

    @staticmethod
    async def hash_password(salt: str, password: str) -> str:
        try:
            ph = argon2.PasswordHasher()
            hashed_password = ph.hash(password + salt)
            return hashed_password
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while hashing password.",
                class_and_method="AuthService.hash_password()",
                argument={'salt': 'anonimized', 'password': 'anonimized'},
                child_error=e,
            )

    @staticmethod
    async def verify_password(salt: bytes, password: str, hash: bytes) -> None:
        try:
            ph = argon2.PasswordHasher()
            is_the_same: bool = ph.verify(hash, password+salt)
            if not is_the_same:
                raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, message="Password not correct.")
        except AuthError as e:
            raise AuthError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="AuthService.verify_password()",
                argument={'salt': 'anonimized', 'password': 'anonimized', 'hash': 'anonimized'}
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while converting jwt payload to jwt payload model.",
                class_and_method="AuthService.verify_password()",
                argument={'salt': 'anonimized', 'password': 'anonimized', 'hash': 'anonimized'},
                child_error=e,
            )

    @staticmethod
    async def jwt_encoder(jwt_data: JWTDataModel) -> str:
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
                message="Unexpected error occured in AuthService while converting jwt payload to jwt payload model.",
                class_and_method="AuthService.jwt_encoder()",
                argument={'jwt_data': jwt_data},
                child_error=e,
            )

    @staticmethod
    async def validate_password(password: str, repeated_password: str) -> bool:
        try:
            if password != repeated_password:
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided passwords are not the same.")
            if len(password) < 8:
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided password is too short.")
            if not re.search(r'[A-Z]', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contatain at least 1 capital letter.")
            if not re.search(r'[a-z]', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contatain at least 1 lowercase letter.")
            if not re.search(r'\d', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contatain at least 1 digit.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Password needs to contatain at least 1 special character.")
            return True
        except LogicError as e:
            raise LogicError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="AuthSevice.validate_password()",
                argument={'password': 'anonimized', 'repeated_password': 'anonimized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while checking does password meets conditions.",
                class_and_method="AuthService.check_does_password_meets_conditions()",
                argument={'password': 'anonimized', 'repeated_password': 'anonimized'},
                child_error=e,
            )

    @staticmethod
    async def validate_email_address(email_address: str, reapeated_email_address: str) -> bool:
        try:
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, email_address):
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided email is in wrong format")
            if email_address != reapeated_email_address:
                raise LogicError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message="Provided email adresses don't match.")
            return True
        except LogicError as e:
            raise LogicError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="AuthSevice.validate_email_address()",
                argument={'email_address': email_address, 'repeated_email_address': reapeated_email_address},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while checking if email has a valid format.",
                class_and_method="AuthService.check_does_email_have_valid_format()",
                argument={'email_address': email_address, 'repeated_email_address': reapeated_email_address},
                child_error=e,
            )

    async def create_and_save_jwt_token(self, user_id: str, email_address: str, jwt_expiration_time: datetime.datetime, salt: str) -> str:
        try:
            jwt_payload: JWTPayloadModel = JWTPayloadModel(
                id=user_id, 
                email=email_address, 
                exp=jwt_expiration_time
                )
            jwt_data: JWTDataModel = JWTDataModel(
                secret=salt, 
                payload=jwt_payload
                )
            jwt_token: str = await self.jwt_encoder(jwt_data)
            await self._user_redis_repository.save_jwt_token(jwt_token, jwt_payload)
            return jwt_token
        except ServiceError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="AuthService.create_and_save_jwt_token()",
                argument={'user_id': user_id, 'email_address': email_address, 'jwt_expiration_time': jwt_expiration_time, 'salt': 'anonimized'},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in AuthService while checking if email has a valid format.",
                class_and_method="AuthService.create_and_save_jwt_token()",
                argument={'user_id': user_id, 'email_address': email_address, 'jwt_expiration_time': jwt_expiration_time, 'salt': 'anonimized'},
                child_error=e,
            )
