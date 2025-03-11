#internal modules
from app.services.auth_service import IAuthService, new_auth_service
from app.custom_exceptions.custom_exceptions import ServiceError
from app.models.authentication_model import LogInModel
from app.models.jwt_model import JWTPayloadModel

#3rd party libraries
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials

#1st party libraries
from typing import Protocol


class ILogoutService(Protocol):

    async def logout(self, login_model: LogInModel) -> str:
        ...
    
    async def logout_from_all_devices(self, token: HTTPAuthorizationCredentials) -> None:
        ...

async def new_logout_service() -> IAuthService:
    try:
        return LogoutService()
    except Exception as e:
        raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while trying create logout service.",
                class_and_method="new_logout_service()",
                argument=None,
                child_error=e
            )

class LogoutService:

    __slots__ = ('auth_service',)

    def __init__(
            self, 
            auth_service: IAuthService = Depends(new_auth_service),
            ):
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
    
    async def logout_from_all_devices(self, token: HTTPAuthorizationCredentials) -> None:
        try:
            jwt_payload: JWTPayloadModel = await self._auth_service.get_jwt(token)
            await self._auth_service.delete_all_jwts(jwt_payload.id)
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
