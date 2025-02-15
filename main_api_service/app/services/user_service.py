#internal modules
from app.database.postgres.repositories.user_repository_interface import IUserPostgresRepository
from app.database.postgres.repositories.user_repository import UserPostgresRepository
from app.database.redis.repositories.user_repository_interface import IUserRedisRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.kafka.events.user_events_interface import IUserEvents
from app.kafka.events.user_events import UserEvents
from app.models.user_model import User, UserModel, CreateUserModel
from app.custom_exceptions.custom_exceptions import (
    DataNotFoundError, 
    ServiceError, 
    DatabaseError
    )
#3rd party libraries
from fastapi import Depends, status

#1st party libraries
from typing import Protocol

class IUserService(Protocol):

    async def get_user_by_id(self, user_id: str) -> UserModel:
        ...

    async def get_user_by_email_address(self, email_address: str) -> User:
        ...

    async def get_user_registration_details_by_email_address(self, email_address: str) -> bytes:
        ...

    async def save_user_registration_data(self, key_id: str, new_user: CreateUserModel) -> None:
        ...

    async def send_user_registration_event(self, key_id: str, email_address: str) -> None:
        ...

    async def confirm_user_account(self, key_id: str) -> None:
        ...

    async def update_last_login_date(self, user_id: str) -> None:
        ...

class UserService:
    def __init__(
            self, 
            user_postgres_repository: IUserPostgresRepository = Depends(UserPostgresRepository),
            user_redis_repository: IUserRedisRepository = Depends(UserRedisRepository),
            user_events: IUserEvents = Depends(UserEvents)
            ):
        self._user_postgres_repository: IUserPostgresRepository = user_postgres_repository
        self._user_redis_repository: IUserRedisRepository = user_redis_repository
        self._user_events: IUserEvents = user_events

    async def get_user_by_id(self, user_id: str) -> UserModel:
        try:
            user: User | None = await self._user_postgres_repository.get_user_by_id(user_id)
            if not user:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message="User not found.")
            return await self._convert_user_schema_to_user_model(user)
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.get_user_by_id()",
                argument={'user_id': user_id},
                child_error=e
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.get_user_by_id()",
                argument={'user_id': user_id},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while getting user by id from database.",
                class_and_method="UserService.get_user_by_id()",
                argument={'user_id': user_id},
                child_error=e,
            )

    @staticmethod
    async def _convert_user_schema_to_user_model(user: User) -> UserModel:
        try:
            return UserModel(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            city=user.city,
            postal_code=user.postal_code,
            street=user.street,
            registration_date=user.registration_date,
            last_login=user.last_login,
            email_notification=user.email_notification,
            push_notification=user.push_notification
        )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while converting user schema to user model.",
                class_and_method="UserService._convert_user_schema_to_user_model()",
                argument={'user': user},
                child_error=e,
            )
        
    async def get_user_by_email_address(self, email_address: str) -> User:
        try:
            user: User | None = await self._user_postgres_repository.get_user_by_email_address(email_address)
            if not user:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message="User with provided email address not found in database.")
            return user
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.get_user_by_email_address()",
                argument={'email_address': email_address},
                child_error=e
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.get_user_by_email_address()",
                argument={'email_address': email_address},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while getting user by email address from database.",
                class_and_method="UserService._convert_user_schema_to_user_model()",
                argument={'user': user},
                child_error=e,
            )
        
    async def get_user_registration_details_by_email_address(self, email_address: str) -> bytes:
        try:
            user_registration_details: bytes | None = await self._user_redis_repository.get_user_registration_data_by_email_address(email_address)
            if not user_registration_details:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message="User registration data not found.")
            return user_registration_details
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="UserService.get_user_registration_details_by_email_address()",
                argument={'email_address': email_address},
                child_error=e
            )
        except DatabaseError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.get_user_registration_details_by_email_address()",
                argument={'email_address': email_address},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while getting user registration data by email address.",
                class_and_method="UserService.get_user_registration_details_by_email_address()",
                argument={'email_address': email_address},
                child_error=e,
            )
        
    async def get_user_registration_details_by_key_id(self, key_id: str) -> bytes:
        try:
            user_registration_details: bytes | None = await self._user_redis_repository.get_user_registration_data_by_id(key_id)
            if not user_registration_details:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message="No confirmation data or account already confirmed.")
            return user_registration_details
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="UserService.get_user_registration_details_by_key_id()",
                argument={'key_id': key_id},
                child_error=e
            )
        except DatabaseError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.get_user_registration_details_by_key_id()",
                argument={'key_id': key_id},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while getting user registration data by key id.",
                class_and_method="UserService.get_user_registration_details_by_key_id()",
                argument={'key_id': key_id},
                child_error=e,
            )
        
    async def save_user_registration_data(self, key_id: str, new_user: CreateUserModel) -> None:
        try:
            await self._user_redis_repository.save_user_registration_data(key_id, new_user)
        except DatabaseError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.save_user_registration_data()",
                argument={'key_id': key_id, 'new_user': 'anonimized'},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while getting saving registration data by email address.",
                class_and_method="UserService.save_user_registration_data()",
                argument={'key_id': key_id, 'new_user': 'anonimized'},
                child_error=e,
            )

    async def send_user_registration_event(self, key_id: str, email_address: str) -> None:
        try:
            await self._user_events.account_registered_event(key_id, email_address)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while sending user registration event.",
                class_and_method="UserService.save_user_registration_data()",
                argument={'key_id': key_id, 'new_user': 'anonimized'},
                child_error=e,
            )

    async def confirm_user_account(self, key_id: str) -> None:
        try:
            user_registration_data: bytes = await self.get_user_registration_details_by_key_id(key_id)
            create_user_model: CreateUserModel = CreateUserModel.model_validate_json(user_registration_data)
            await self._user_postgres_repository.create_user(create_user_model)
            await self._user_redis_repository.delete_user_registration_data_by_id(key_id)
            await self._user_events.account_confirmed_event(create_user_model.email)
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="UserService.confirm_user_account()",
                argument={'key_id': key_id},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while confirming user account.",
                class_and_method="UserService.save_user_registration_data()",
                argument={'key_id': key_id, 'new_user': 'anonimized'},
                child_error=e,
            )
        
    async def update_last_login_date(self, user_id: str) -> None:
        try:
            await self._user_postgres_repository.update_user_last_login(user_id)
        except Exception as e:
            pass
    
