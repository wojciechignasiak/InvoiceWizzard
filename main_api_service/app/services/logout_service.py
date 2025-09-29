#internal modules
from main_api_service.app.services.auth_service import IAuthService, new_auth_service
from main_api_service.app.custom_exceptions.custom_exceptions import ServiceError
from main_api_service.app.models.jwt_model import JWTPayloadModel

#3rd party libraries
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials

#1st party libraries
from typing import Protocol


class ILogoutService(Protocol):

    async def logout(self, token: HTTPAuthorizationCredentials) -> None:
        ...
    
    async def logout_from_all_devices(self, token: HTTPAuthorizationCredentials) -> None:
        ...

def new_logout_service(
    auth_service: IAuthService = Depends(new_auth_service)
) -> ILogoutService:
    try:
        return LogoutService(
            auth_service,
        )
    except Exception as e:
        raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while trying create logout service",
                argument=None,
                child_error=e
            )

class LogoutService(ILogoutService):

    __slots__ = ('auth_service',)

    def __init__(
            self, 
            auth_service: IAuthService,
            ):
        self._auth_service: IAuthService = auth_service

    async def logout(self, token: HTTPAuthorizationCredentials) -> None:
        try:
            await self._auth_service.delete_jwt(str(token))
        except ServiceError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.args[0],
                argument={'token': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in LogoutService while trying to logout user",
                argument={'token': 'anonymized'},
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
                argument={'token': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in LogoutService while trying to logout user",
                argument={'token': 'anonymized'},
                child_error=e
            )
