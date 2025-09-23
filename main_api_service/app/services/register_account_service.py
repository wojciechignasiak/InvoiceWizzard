#internal modules
from main_api_service.app.services.user_service import IUserService, new_user_service
from main_api_service.app.services.auth_service import IAuthService, new_auth_service
from main_api_service.app.models.user_model import (
    RegisterUserModel,
    CreateUserModel
)
from main_api_service.app.schema.schema import User
from main_api_service.app.custom_exceptions.custom_exceptions import (
    DataNotFoundError,
    ServiceError,
    DatabaseError,
    LogicError
)

#3rd party libraries
from fastapi import Depends, status

#1st party libraries
import uuid
from typing import Protocol


class IRegisterAccountService(Protocol):

    async def register_user(self, register_user_model: RegisterUserModel) -> None:
        ...

    async def _check_is_email_already_taken(self, email_address: str) -> None:
        ...

    async def _check_is_email_already_registered(self, email_address: str) -> None:
        ...

def new_register_account_service() -> IRegisterAccountService:
    try:
        return RegisterAccountService()
    except Exception as e:
        raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while creating register account service.",
                argument=None,
                child_error=e,
            )

class RegisterAccountService(IRegisterAccountService):

    __slots__ = ('user_service', 'auth_service',)

    def __init__(
            self, 
            user_service: IUserService = Depends(new_user_service),
            auth_service: IAuthService = Depends(new_auth_service),
            ):
        self._user_service: IUserService = user_service
        self._auth_service: IAuthService = auth_service

    async def register_user(self, register_user_model: RegisterUserModel, key_id: uuid.UUID = uuid.uuid4()) -> None:
        try:
            self._auth_service.validate_email_address(register_user_model.email_address, register_user_model.repeated_email)
            await self._check_is_email_already_taken(register_user_model.email)
            await self._check_is_email_already_registered(register_user_model.email)
            self._auth_service.validate_password(register_user_model.password, register_user_model.repeated_password)
            salt: str = self._auth_service.salt_generator()
            hashed_password: str = self._auth_service.hash_password(salt, register_user_model.password)
            create_user_model: CreateUserModel = CreateUserModel(
                email=register_user_model.email,
                password=hashed_password,
                salt=salt
            )
            await self._user_service.save_user_registration_data(key_id, create_user_model)
            await self._user_service.send_user_registration_event(key_id, register_user_model.email)
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                argument={'register_user_model':  self.__anonymize_user_password_and_email_for_exception(register_user_model)},
                child_error=e
            )
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'register_user_model':  self.__anonymize_user_password_and_email_for_exception(register_user_model)},
                child_error=e,
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'register_user_model':  self.__anonymize_user_password_and_email_for_exception(register_user_model)},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in RegisterAccountService while registering user",
                argument={'register_user_model': self.__anonymize_user_password_and_email_for_exception(register_user_model)},
                child_error=e,
            )

    async def _check_is_email_already_taken(self, email_address: str) -> None:
        try:
            user: User | None = await self._user_service.get_user_by_email_address(email_address)
            if user:
                raise LogicError(status_code=status.HTTP_409_CONFLICT, message="Email address already in use")
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'email_address': email_address},
                child_error=e,
            )
        except DataNotFoundError:
            return None
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'email_address': email_address},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in RegisterUserService while checking is email address already taken",
                argument={'email_address': email_address},
                child_error=e,
            )

    async def _check_is_email_already_registered(self, email_address: str) -> None:
        try:
            user: bytes | None = await self._user_service.get_user_registration_details_by_email_address(email_address)
            if user:
                raise LogicError(status_code=status.HTTP_409_CONFLICT, message="Account with provided email address is already registered. Please confirm your email address")
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'email_address': email_address},
                child_error=e,
            )
        except DataNotFoundError:
            return None
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'email_address': email_address},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in RegisterUserService while checking is email address already taken.",
                argument={'email_address': email_address},
                child_error=e,
            )

    @staticmethod
    def __anonymize_user_password_and_email_for_exception(register_user_model: RegisterUserModel) -> RegisterUserModel:
        register_user_model.password = 'anonymized'
        register_user_model.repeated_password = 'anonymized'
        return register_user_model
