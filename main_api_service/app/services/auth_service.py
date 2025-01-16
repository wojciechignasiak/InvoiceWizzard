#internal modules
from app.database.redis.repositories.user_repository_interface import IUserRedisRepository
from app.database.redis.repositories.user_repository import UserRedisRepository
from app.models.jwt_model import (
    JWTDataModel, 
    JWTPayloadModel
)
from app.custom_exceptions.custom_exceptions import (AuthError, ServiceError, DatabaseError)

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends, status

class AuthService:

    def __init__(
            self, 
            user_redis_repository: IUserRedisRepository = Depends(UserRedisRepository)
            ):
        self._user_redis_repository: IUserRedisRepository = user_redis_repository
        
    async def get_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        try:
            jwt_payload: bytes | None = await self._user_redis_repository.retrieve_jwt(token.credentials)
            if not jwt_payload:
                raise AuthError(status_code=status.HTTP_401_UNAUTHORIZED, message="Unauthorized access or token expired")
            return await self.conver_jwt_payload_to_jwt_payload_model(jwt_payload)
        except AuthError as e:
            raise e
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                class_and_method="AuthService.get_jwt()",
                argument={'token': token},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while getting JWT token from database.",
                class_and_method="AuthService.get_jwt()",
                argument={'token': token},
                child_error=e,
            )
    
    @staticmethod
    async def _conver_jwt_payload_to_jwt_payload_model(jwt_payload: bytes) -> JWTPayloadModel:
        try:
            return JWTPayloadModel.model_validate_json(jwt_payload)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in AuthService while converting jwt payload to jwt payload model.",
                class_and_method="AuthService.conver_jwt_payload_to_jwt_payload_model()",
                argument={'jwt_payload': jwt_payload},
                child_error=e,
            )

