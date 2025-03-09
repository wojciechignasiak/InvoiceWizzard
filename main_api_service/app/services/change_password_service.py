#internal modules
from app.services.user_service import IUserService, new_user_service
from app.services.auth_service import IAuthService, new_auth_service
from app.custom_exceptions.custom_exceptions import AuthError, DataNotFoundError, ServiceError
from app.models.user_model import (
    UpdateUserPasswordModel, 
    ConfirmedUserPasswordChangeModel, 
    ResetUserPasswordModel
)
from app.models.jwt_model import JWTPayloadModel
from app.schema.schema import User

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends, status

#1st party libraries
from typing import Protocol



class IChangePasswordService(Protocol):

    async def change_password(self, token: HTTPAuthorizationCredentials, new_password: UpdateUserPasswordModel) -> None:
        ...

    async def reset_password(self, reset_password: ResetUserPasswordModel) -> None:
        ...

async def new_change_password_service() -> IAuthService:
    try:
        return ChangePasswordService()
    except Exception as e:
        raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while creating new change password service.",
                class_and_method="new_change_password_service()",
                argument=None,
                child_error=e
            )

class ChangePasswordService:

    __slots__ = ('user_service', 'auth_service',)

    def __init__(
            self, 
            user_service: IUserService = Depends(new_user_service),
            auth_service: IAuthService = Depends(new_auth_service),
            ):
        self._user_service: IUserService = user_service
        self._auth_service: IAuthService = auth_service

    async def change_password(self, token: HTTPAuthorizationCredentials, new_password: UpdateUserPasswordModel) -> None:
        try:
            jwt_payload: JWTPayloadModel = await self._auth_service.get_jwt(token)
            user: User = await self._user_service.get_user_by_id(jwt_payload.id)
            await self._auth_service.verify_password(user.salt, new_password.current_password, user.password)
            await self._auth_service.validate_password(new_password.new_password, new_password.new_repeated_password)
            salt: str = await self._auth_service.salt_generator()
            hashed_new_password: str = await self._auth_service.hash_password(salt, new_password.new_password)
            new_password_data: ConfirmedUserPasswordChangeModel = ConfirmedUserPasswordChangeModel(
                id=str(user.id),
                new_password=hashed_new_password,
                salt=salt
            )
            await self._user_service.change_password(user.email, new_password_data)
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="ChangePasswordService.change_password()",
                argument={'token': 'anonymized', 'new_password': 'anonymized'},
                child_error=e
            )
        except (ServiceError, AuthError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="ChangePasswordService.change_password()",
                argument={'token': 'anonymized', 'new_password': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in ChangePasswordService while changing password.",
                class_and_method="ChangePasswordService.change_password()",
                argument={'token': 'anonymized', 'new_password': 'anonymized'},
                child_error=e
            )

    async def reset_password(self, reset_password: ResetUserPasswordModel) -> None:
        try:
            user: User = await self._user_service.get_user_by_email_address(reset_password.email)
            await self._auth_service.validate_password(reset_password.new_password, reset_password.new_repeated_password)
            salt: str = await self._auth_service.salt_generator()
            hashed_new_password: str = await self._auth_service.hash_password(salt, reset_password.new_password)
            new_password_data: ConfirmedUserPasswordChangeModel = ConfirmedUserPasswordChangeModel(
                id=str(user.id), 
                new_password=hashed_new_password,
                salt=salt
                )
            await self._user_service.reset_password(user.email, new_password_data)
        except DataNotFoundError:
            return None
        except ServiceError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="ChangePasswordService.reset_password()",
                argument={'token': 'anonymized', 'new_password': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in ChangePasswordService while reseting password.",
                class_and_method="ChangePasswordService.reset_password()",
                argument={'token': 'anonymized', 'new_password': 'anonymized'},
                child_error=e
            )