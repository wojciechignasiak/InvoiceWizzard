#internal modules
from app.services.user_service_interface import IUserService
from app.services.user_service import UserService
from app.services.auth_service_interface import IAuthService
from app.services.auth_service import AuthService
from app.models.user_model import (
    User, 
    RegisterUserModel, 
    CreateUserModel
)
from app.custom_exceptions.custom_exceptions import (
    DataNotFoundError,
    ServiceError,
    DatabaseError,
    LogicError
)

#3rd party libraries
from fastapi import Depends, status

#1st party libraries
from uuid import uuid4

class RegisterAccountService:
    def __init__(
            self, 
            user_service: IUserService = Depends(UserService),
            auth_service: IAuthService = Depends(AuthService),
            ):
        self._user_service: IUserService = user_service
        self._auth_service: IAuthService = auth_service

    async def register_user(self, register_user_model: RegisterUserModel) -> None:
        try:
            await self._auth_service.validate_email_address(register_user_model.email_address, register_user_model.repeated_email)
            await self._check_is_email_arleady_taken(register_user_model.email)
            await self._check_is_email_arleady_registered(register_user_model.email)
            await self._auth_service.validate_password(register_user_model.password, register_user_model.repeated_password)
            salt: str = await self._auth_service.salt_generator()
            hashed_passwrod: str = await self._auth_service.hash_password(salt, register_user_model.password)
            key_id: str = str(uuid4())
            create_user_model: CreateUserModel = CreateUserModel(
                email=register_user_model.email,
                password=hashed_passwrod,
                salt=salt
            )
            await self._user_service.save_user_registration_data(key_id, create_user_model)
            await self._user_service.send_user_registration_event(key_id, register_user_model.email)
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.args[0],
                message=e.message,
                class_and_method="RegisterAccountService.register_user()",
                argument={'register_user_model':  await self.__anonimize_user_password_and_email_for_exception(register_user_model)},
                child_error=e
            )
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="RegisterAccountService.register_user()",
                argument={'register_user_model':  await self.__anonimize_user_password_and_email_for_exception(register_user_model)},
                child_error=e,
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="RegisterAccountService.register_user()",
                argument={'register_user_model':  await self.__anonimize_user_password_and_email_for_exception(register_user_model)},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in RegisterAccountService while registering user.",
                class_and_method="RegisterAccountService.register_user()",
                argument={'register_user_model': await self.__anonimize_user_password_and_email_for_exception(register_user_model)},
                child_error=e,
            )

    async def _check_is_email_arleady_taken(self, email_address: str) -> None:
        try:
            user: User | None = await self._user_service.get_user_by_email_address(email_address)
            if user:
                raise LogicError(status_code=status.HTTP_409_CONFLICT, message="Email address already in use.")
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="RegisterAccountService.check_is_email_arleady_taken()",
                argument={'email_address': email_address},
                child_error=e,
            )
        except DataNotFoundError:
            return None
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="RegisterAccountService.check_is_email_arleady_taken()",
                argument={'email_address': email_address},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in RegisterUserService while checking is email address arleady taken.",
                class_and_method="RegisterAccountService.check_is_email_arleady_taken()",
                argument={'email_address': email_address},
                child_error=e,
            )

    async def _check_is_email_arleady_registered(self, email_address: str) -> None:
        try:
            user: User | None = await self._user_service.get_user_registration_details_by_email_address(email_address)
            if user:
                raise LogicError(status_code=status.HTTP_409_CONFLICT, message="Account with provided email address is already registered. Please confirm your email address.")
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="RegisterAccountService._check_is_email_arleady_registered()",
                argument={'email_address': email_address},
                child_error=e,
            )
        except DataNotFoundError:
            return None
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="RegisterAccountService._check_is_email_arleady_registered()",
                argument={'email_address': email_address},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in RegisterUserService while checking is email address arleady taken.",
                class_and_method="RegisterAccountService._check_is_email_arleady_registered()",
                argument={'email_address': email_address},
                child_error=e,
            )

    @staticmethod
    async def __anonimize_user_password_and_email_for_exception(register_user_model: RegisterUserModel) -> RegisterUserModel:
        register_user_model.password = 'anonimized'
        register_user_model.repeated_password = 'anonimized'
        return register_user_model
