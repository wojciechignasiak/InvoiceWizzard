#internal modules
from app.services.user_service import IUserService, UserService
from app.services.auth_service import IAuthService, AuthService
from app.custom_exceptions.custom_exceptions import AuthError, DataNotFoundError, ServiceError
from app.models.authentication_model import LogInModel
from app.schema.schema import User

#3rd party libraries
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials

#1st party libraries
import datetime
from typing import Protocol

#internal modules
from app.models.jwt_model import JWTPayloadModel


class ILogoutService(Protocol):

    async def logout(self, login_model: LogInModel) -> str:
        ...

class LogoutService:
    def __init__(
            self, 
            user_service: IUserService = Depends(UserService),
            auth_service: IAuthService = Depends(AuthService),
            ):
        self._user_service: IUserService = user_service
        self._auth_service: IAuthService = auth_service

    async def logout(self, token: HTTPAuthorizationCredentials) -> None:
        try:
            await self._auth_service.delete_jwt(str(token))
        except ServiceError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="LogoutService.logout()",
                argument={'token': 'anonimized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in LogoutService while trying to logout user.",
                class_and_method="LogoutService.logout()",
                argument={'token': 'anonimized'},
                child_error=e
            )
