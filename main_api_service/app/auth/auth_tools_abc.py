from app.models.jwt_model import JWTDataModel
from abc import ABC, abstractmethod

class AuthToolsABC(ABC):
    
    @abstractmethod
    async def salt_generator(self) -> str:
        ...

    @abstractmethod
    async def hash_password(self, salt: str, password: str) -> str:
        ...

    @abstractmethod
    async def verify_password(self, salt: str, password: str, hash: str) -> bool:
        ...

    @abstractmethod
    async def jwt_encoder(self, jwt_data: JWTDataModel) -> str:
        ...