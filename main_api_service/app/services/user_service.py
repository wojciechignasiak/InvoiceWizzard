#internal modules
from app.database.postgres.repositories.user_repository import IUserPostgresRepository, new_user_postgres_repository
from app.database.redis.repositories.user_repository import IUserRedisRepository, new_user_redis_repository
from app.kafka.events.user_events import IUserEvents, new_user_events
from app.models.user_model import (
    UserModel,
    CreateUserModel,
    UserPersonalInformationModel,
    UpdateUserEmailModel,
    ConfirmedUserEmailChangeModel,
    ConfirmedUserPasswordChangeModel
)
from app.schema.schema import User
from app.custom_exceptions.custom_exceptions import (
    DataNotFoundError, 
    ServiceError, 
    DatabaseError,
    EventError,
    )

#3rd party libraries
from fastapi import Depends, status

#1st party libraries
from typing import Protocol
from uuid import uuid4


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

    async def update_user_personal_informations(self, user_id: str, personal_informations: UserPersonalInformationModel) -> None:
        ...

    async def change_email_address(user_id: str, update_email_address: UpdateUserEmailModel) -> None:
        ...

    async def confirm_email_address_change(self, key_id: str) -> None:
        ...

    async def change_password(self, email_address: str, new_password: ConfirmedUserPasswordChangeModel, key_id: str = str(uuid4())):
        ...

    async def reset_password(self, email_address: str, new_password: ConfirmedUserPasswordChangeModel, key_id: str = str(uuid4)):
        ...

    async def confirm_password_change(self, key_id: str) -> None:
        ...

async def new_user_service() -> IUserService:
    try:
        return UserService()
    except Exception as e:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error occured in while creating user service.",
            class_and_method="new_user_service()",
            argument=None,
            child_error=e,
        )

class UserService:

    __slots__ = ('user_postgres_repository', 'user_redis_repository', 'user_events',)

    def __init__(
            self, 
            user_postgres_repository: IUserPostgresRepository = Depends(new_user_postgres_repository),
            user_redis_repository: IUserRedisRepository = Depends(new_user_redis_repository),
            user_events: IUserEvents = Depends(new_user_events)
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
            await self._user_events.account_registered(key_id, email_address)
        except EventError as e:
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
            await self._user_events.account_confirmed(create_user_model.email)
        except EventError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.confirm_user_account()",
                argument={'key_id': key_id},
                child_error=e,
            )
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
        except DatabaseError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.update_last_login_date()",
                argument={'user_id': user_id},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while updating user last login date.",
                class_and_method="UserService.update_last_login_date()",
                argument={'user_id': user_id},
                child_error=e,
            )
    
    async def update_user_personal_informations(self, user_id: str, personal_informations: UserPersonalInformationModel) -> None:
        try:
            await self._user_postgres_repository.update_user_personal_information(user_id, personal_informations)
        except DatabaseError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="UserService.update_user_personal_information()",
                argument={'user_id': user_id, 'personal_informations': 'anonymized'},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in UserService while updating user personal informations.",
                class_and_method="UserService.update_user_personal_information()",
                argument={'user_id': user_id, 'personal_informations': 'anonymized'},
                child_error=e,
            )
    
    async def change_email_address(self, user_id: str, update_email_address: UpdateUserEmailModel, key_id: str = str(uuid4())) -> None:
        try:
            if update_email_address.new_email != update_email_address.new_repeated_email:
                raise ServiceError(status_code=status.HTTP_400_BAD_REQUEST, message="Provided emails are not the same.")
            
            user: UserModel = await self._user_postgres_repository.get_user_by_id(user_id)

            if user.email != update_email_address.current_email:
                raise ServiceError(status_code=status.HTTP_400_BAD_REQUEST, message="Provided current email is not the same as already used one.")
            if user.email == update_email_address.new_email:
                raise ServiceError(status_code=status.HTTP_401_UNAUTHORIZED, message="New email address is the same as currently used one.")

            user_that_is_already_using_email_address: UserModel | None = await self._user_postgres_repository.get_user_by_email_address(update_email_address.new_email)
            if user_that_is_already_using_email_address is not None:
                raise ServiceError(status_code=status.HTTP_409_CONFLICT, message="Provided new email address arleady in use.")
            
            new_email_data: ConfirmedUserEmailChangeModel = ConfirmedUserEmailChangeModel(
            id=user.id, 
            new_email=update_email_address.new_email
            )
            
            await self._user_redis_repository.save_new_email(key_id, new_email_data)
            await self._user_events.change_email(key_id, user.email)
        except (ServiceError, DatabaseError, EventError) as e:
            raise ServiceError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.change_email_address()",
                argument={'user_id': user_id, 'update_email_address': update_email_address},
                child_error=e
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.change_email_address()",
                argument={'user_id': user_id, 'update_email_address': update_email_address},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code="Unexpected error occurred in UserService while changing email.",
                message=e.message,
                class_and_method="UserService.change_email_address()",
                argument={'user_id': user_id, 'update_email_address': update_email_address},
                child_error=e
            )

    async def confirm_email_address_change(self, key_id: str) -> None:
        try:
            new_email_data: bytes | None = await self._user_redis_repository.retrieve_new_email(key_id)
            if new_email_data is None:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message="Change email expired or new has never been set.")
            new_email_data: ConfirmedUserEmailChangeModel = ConfirmedUserEmailChangeModel.model_validate_json(new_email_data)
            user: User | None = await self._user_postgres_repository.get_user_by_email_address(new_email_data.new_email)
            if user is not None:
                raise ServiceError(status_code=status.HTTP_409_CONFLICT, message="Provided new email address arleady in use.")
            
            await self._user_postgres_repository.update_user_email_address(new_email_data.id)
            await self._user_redis_repository.delete_all_jwt_tokens_of_user(new_email_data.id)
            await self._user_redis_repository.delete_new_email(key_id)
            await self._user_events.email_changed(new_email_data.new_email)
        except (ServiceError, DatabaseError, EventError) as e:
            raise ServiceError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.confirm_email_address_change()",
                argument={'key_id': key_id},
                child_error=e
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.confirm_email_address_change()",
                argument={'key_id': key_id},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code="Unexpected error occurred in UserService while confirming email change.",
                message=e.message,
                class_and_method="UserService.confirm_email_address_change()",
                argument={'key_id': key_id},
                child_error=e
            )
        
    async def change_password(self, email_address: str, new_password: ConfirmedUserPasswordChangeModel, key_id: str = str(uuid4())):
        try:
            await self._user_redis_repository.save_new_password(key_id, new_password)
            await self._user_events.change_password(key_id, email_address)
        except (ServiceError, DatabaseError, EventError) as e:
            raise ServiceError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.change_password()",
                argument={'email_address': email_address, 'key_id': key_id, 'new_password': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code="Unexpected error occurred in UserService while changing password.",
                message=e.message,
                class_and_method="UserService.change_password()",
                argument={'email_address': email_address, 'key_id': key_id, 'new_password': 'anonymized'},
                child_error=e
            )
        
    async def reset_password(self, email_address: str, new_password: ConfirmedUserPasswordChangeModel, key_id: str = str(uuid4)):
        try:
            await self._user_redis_repository.save_new_password(key_id, new_password)
            await self._user_events.reset_password(key_id, new_password)
        except (ServiceError, DatabaseError, EventError) as e:
            raise ServiceError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.reset_password()",
                argument={'email_address': email_address, 'key_id': key_id, 'new_password': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code="Unexpected error occurred in UserService while reseting password.",
                message=e.message,
                class_and_method="UserService.reset_password()",
                argument={'email_address': email_address, 'key_id': key_id, 'new_password': 'anonymized'},
                child_error=e
            )
        
    async def confirm_password_change(self, key_id: str) -> None:
        try:
            new_password_data: bytes | None = await self._user_redis_repository.get_new_password(key_id)
            if new_password_data is None:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message="Password change expired or has never been set.")
            new_password_data: ConfirmedUserPasswordChangeModel = ConfirmedUserPasswordChangeModel.model_validate_json(new_password_data)
            user: User = await self.get_user_by_id(new_password_data.id)
            await self._user_postgres_repository.update_user_password(new_password_data.new_password)
            await self._user_redis_repository.delete_all_jwt_tokens_of_user(new_password_data.id)
            await self._user_redis_repository.delete_new_password(key_id)
            await self._user_events.password_changed(user.email)
        except (ServiceError, DatabaseError, EventError) as e:
            raise ServiceError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.confirm_password_change()",
                argument={'key_id': key_id},
                child_error=e
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="UserService.confirm_password_change()",
                argument={'key_id': key_id},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code="Unexpected error occurred in UserService while confirming password change.",
                message=e.message,
                class_and_method="UserService.confirm_password_change()",
                argument={'key_id': key_id},
                child_error=e
            )