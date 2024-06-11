from abc import ABC, abstractmethod
from app.services.user_service_abc import UserServiceABC
from app.services.auth_service_abc import AuthServiceABC

class ServicesFactoryABC(ABC):
    
    @abstractmethod
    async def get_auth_service(self) -> AuthServiceABC:
        pass
    
    @abstractmethod
    async def get_user_service(self) -> UserServiceABC:
        pass