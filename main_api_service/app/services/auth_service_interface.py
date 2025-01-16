#internal modules
from app.models.jwt_model import (
    JWTPayloadModel
)

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials

#1st party libraries
from typing import Protocol

class IAuthService(Protocol):
        
    async def get_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        ...