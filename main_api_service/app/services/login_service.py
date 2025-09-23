#internal modules
from main_api_service.app.services.user_service import IUserService, UserService
from main_api_service.app.services.auth_service import IAuthService, AuthService
from main_api_service.app.custom_exceptions.custom_exceptions import AuthError, DataNotFoundError, ServiceError
from main_api_service.app.models.authentication_model import LogInModel
from main_api_service.app.schema.schema import User

#3rd party libraries
from fastapi import Depends, status

#1st party libraries
import datetime
from typing import Protocol



class ILoginService(Protocol):

    async def login(self, login_model: LogInModel) -> str:
        ...

    @staticmethod
    def set_jwt_expiration_time(remember_me: bool) -> datetime.datetime:
        ...

def new_login_service() -> ILoginService:
    try:
        return LoginService()
    except Exception as e:
        raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while creating login service",
                argument=None,
                child_error=e
            )

class LoginService(ILoginService):

    __slots__ = ('user_service', 'auth_service',)

    def __init__(
            self, 
            user_service: IUserService = Depends(UserService),
            auth_service: IAuthService = Depends(AuthService),
            ):
        self._user_service: IUserService = user_service
        self._auth_service: IAuthService = auth_service

    async def login(self, login_model: LogInModel) -> str:
        try:
            user: User = await self._user_service.get_user_by_email_address(login_model.email)
            self._auth_service.verify_password(user.salt, login_model.password, user.password)
            jwt_expiration_time: datetime.datetime = self.set_jwt_expiration_time(login_model.remember_me)
            jwt_token: str = await self._auth_service.create_and_save_jwt_token(user.id, user.email, jwt_expiration_time, user.salt)
            await self._user_service.update_last_login_date(user.id)
            return jwt_token
        except AuthError as e:
            raise AuthError(
                status_code=e.status_code,
                message=e.args[0],
                argument={'log_in_model': 'anonymized'},
                child_error=e
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.args[0],
                argument={'log_in_model': 'anonymized'},
                child_error=e
            )
        except ServiceError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.args[0],
                argument={'log_in_model': 'anonymized'},
                child_error=e
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in LogInService while trying to log in user",
                argument={'log_in_model': 'anonymized'},
                child_error=e
            )

    @staticmethod
    def set_jwt_expiration_time(remember_me: bool) -> datetime.datetime:
        try:
            if remember_me:
                return datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24*14)
            else:
                return datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=12)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in LogInService while setting jwt token expiration time",
                argument={'remember_me': remember_me},
                child_error=e
            )
    
