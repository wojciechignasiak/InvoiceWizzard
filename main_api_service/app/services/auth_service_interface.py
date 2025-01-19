#internal modules
from app.models.jwt_model import (
    JWTPayloadModel,
    JWTDataModel
)

#3rd party libraries
from fastapi.security import HTTPAuthorizationCredentials

#1st party libraries
from typing import Protocol

class IAuthService(Protocol):
        
    async def get_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        ...

    async def salt_generator() -> str:
        ...
    
    async def hash_password(salt: str, password: str) -> str:
        ...

    async def verify_password(salt: bytes, password: str, hash: bytes) -> bool:
        ...

    async def jwt_encoder(jwt_data: JWTDataModel) -> str:
        ...

    async def validate_password(password: str, repeated_password: str) -> bool:
        ...
    
    async def validate_email_address(email_address: str, reapeated_email_address: str) -> bool:
        ...