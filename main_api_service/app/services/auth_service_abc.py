from abc import ABC, abstractmethod
from app.models.jwt_model import JWTPayloadModel
from app.models.jwt_model import JWTDataModel
from fastapi.security import HTTPAuthorizationCredentials


class AuthServiceABC(ABC):
    
    @abstractmethod
    async def get_user_jwt(self, token: HTTPAuthorizationCredentials) -> JWTPayloadModel:
        pass

    @abstractmethod
    async def salt_generator(self) -> str:
        pass

    @abstractmethod
    async def hash_password(self, salt: str, password: str) -> str:
        pass

    @abstractmethod
    async def verify_password(self, salt: str, password: str, hash: str) -> bool:
        pass

    @abstractmethod
    async def jwt_encoder(self, jwt_data: JWTDataModel) -> str:
        pass