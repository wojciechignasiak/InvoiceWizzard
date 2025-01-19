import datetime
from app.database.redis.repositories.base_redis_repository import BaseRedisRepository
from app.models.user_model import (
    CreateUserModel, 
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )

from app.custom_exceptions.custom_exceptions import DatabaseError
from app.models.jwt_model import JWTPayloadModel


from fastapi import status


class UserRedisRepository(BaseRedisRepository):

    async def save_user_registration_data(self, key_id: str, new_user: CreateUserModel) -> None:
        try:
            expiry_time = datetime.timedelta(days=14)
            is_user_created: bool = await self.redis_client.set(
                name=f"user:{key_id}:{str(new_user.email)}",
                value=new_user.model_dump_json(),
                ex=expiry_time
            )
            if is_user_created is False:
                raise DatabaseError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Cannot register new user in database.")
        except DatabaseError as e:
            raise DatabaseError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="UserRedisRepository.add_user_registration_data()",
                argument={'anonimized': 'anonimized'},
                child_error=e
            )
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserRedisRepository while saving user registration data.",
                class_and_method="UserRedisRepository.save_user_registration_data()",
                argument={'anonimized': 'anonimized'},
                child_error=e
            )

    async def get_user_registration_data_by_id(self, key_id: str) -> bytes | None:
        try:
            user_key: list[bytes] = await self.redis_client.keys(f"user:{key_id}:*")
            if user_key:
                return await self.redis_client.get(user_key[0])
            else:
                return None
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserRedisRepository while saving user registration data by id.",
                class_and_method="UserRedisRepository.get_user_registration_data_by_id()",
                argument={'key_id': key_id},
                child_error=e
            )

    async def get_user_registration_data_by_email_address(self, email_address: str) -> bytes | None:
        try:
            user_key: list[bytes] = await self.redis_client.keys(f"user:*:{email_address}")
            if user_key:
                return await self.redis_client.get(user_key[0])
            else:
                return None
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserRedisRepository while getting user registration data by email address.",
                class_and_method="UserRedisRepository.get_user_registration_data_by_email_address()",
                argument={'email_address': email_address},
                child_error=e
            )
        
    async def delete_user_registration_data_by_id(self, key_id: str) -> None:
        try:
            user_key: list = await self.redis_client.keys(f"user:{key_id}:*")
            if user_key:
                await self.redis_client.delete(user_key[0])
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserRedisRepository while deleting user registration data by email address.",
                class_and_method="UserRedisRepository.delete_user_registration_data_by_id()",
                argument={'key_id': key_id},
                child_error=e
            )
        
    async def save_jwt_token(self, jwt_token: str, jwt_payload: JWTPayloadModel) -> None:
        try:
            expiry_time = jwt_payload.exp - datetime.datetime.now(datetime.UTC)
            is_jwt_saved: bool = await self.redis_client.set(
                name=f"JWT:{jwt_token}:{jwt_payload.id}",
                value=jwt_payload.model_dump_json(),
                ex=expiry_time)
            if is_jwt_saved is False:
                raise DatabaseError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unexpected error occured in UserRedisRepository durning saving JWT Token.")
        except DatabaseError as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=e.args[0],
                class_and_method="UserRedisRepository.save_jwt_token()",
                argument={'jwt_token': 'anonimized', 'jwt_payload': 'anonimized'},
                child_error=e
            )
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserRedisRepository while saving JWT token.",
                class_and_method="UserRedisRepository.save_jwt_token()",
                argument={'jwt_token': 'anonimized', 'jwt_payload': 'anonimized'},
                child_error=e
            )
    
    async def get_jwt_token(self, jwt_token: str) -> bytes | None:
        try:
            jwt_token_key: list = await self.redis_client.keys(f"JWT:{jwt_token}:*")
            if jwt_token_key:
                result = await self.redis_client.get(jwt_token_key[0])
                return result
            else:
                return None
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning getting user jwt token from Redis database.",
                class_and_method="UserRedisRepository.get_jwt_token()",
                argument={'jwt_token': 'anonimized'},
                child_error=e
            )
        
    async def delete_all_jwt_tokens_of_user(self, user_id: str) -> None:
        try:
            jwt_token_keys: list = await self.redis_client.keys(f"JWT:*:{user_id}")
            if jwt_token_keys:
                for token_key in jwt_token_keys:
                    await self.redis_client.delete(token_key)
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning deleting all user jwt token from Redis database.",
                class_and_method="UserRedisRepository.get_jwt_token()",
                argument={'user_id': user_id},
                child_error=e
            )
        
    async def delete_jwt_token(self, user_id: str, token: str) -> None:
        try:
            await self.redis_client.delete(f"JWT:{token}:{user_id}")
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning deleting user jwt token from Redis database.",
                class_and_method="UserRedisRepository.get_jwt_token()",
                argument={'user_id': user_id, 'token': 'anonimized'},
                child_error=e
            )
        
    async def save_new_email(self, key_id: str, new_email: ConfirmedUserEmailChangeModel) -> None:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_new_email_saved: bool = await self.redis_client.set(
                name=f"new_email:{key_id}", 
                value=new_email.model_dump_json(),
                ex=expiry_time)
            if is_new_email_saved is False:
                raise DatabaseError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unexpected error occured in UserRedisRepository durning saving new email address.")
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning saving new email address.",
                class_and_method="UserRedisRepository.save_new_email()",
                argument={'key_id': key_id, 'new_email': new_email},
                child_error=e
            )
        
    async def retrieve_new_email(self, key_id: str) -> bytes | None:
        try:
            new_email: bytes | None = await self.redis_client.get(f"new_email:{key_id}")
            return new_email
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning saving new email address.",
                class_and_method="UserRedisRepository.save_new_email()",
                argument={'key_id': key_id, 'new_email': new_email},
                child_error=e
            )
        
    async def delete_new_email(self, key_id: str) -> None:
        try:
            await self.redis_client.delete(f"new_email:{key_id}")
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning deleting new email address.",
                class_and_method="UserRedisRepository.delete_new_email()",
                argument={'key_id': key_id},
                child_error=e
            )
        
    async def save_new_password(self, key_id: str, new_password: ConfirmedUserPasswordChangeModel) -> None:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_new_password_saved: bool = await self.redis_client.set(
                name=f"new_password:{key_id}", 
                value=new_password.model_dump_json(),
                ex=expiry_time)
            if is_new_password_saved is False:
                raise DatabaseError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unexpected error occured in UserRedisRepository durning saving new password.")
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning saving new email address.",
                class_and_method="UserRedisRepository.save_new_password()",
                argument={'key_id': key_id, 'new_password': 'anonimized'},
                child_error=e
            )
        
    async def get_new_password(self, key_id: str) -> bytes | None:
        try:
            new_password: bytes | None = await self.redis_client.get(f"new_password:{key_id}")
            return new_password
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning saving new email address.",
                class_and_method="UserRedisRepository.save_new_password()",
                argument={'key_id': key_id},
                child_error=e
            )
        
    async def delete_new_password(self, key_id: str) -> None:
        try:
            await self.redis_client.delete(f"new_password:{key_id}")
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Unexpected error occurred in UserRedisRepository durning deleting new password.",
                class_and_method="UserRedisRepository.delete_new_password()",
                argument={'key_id': key_id},
                child_error=e
            )