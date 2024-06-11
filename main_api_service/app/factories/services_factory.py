from app.services.user_service_abc import UserServiceABC
from app.services.auth_service_abc import AuthServiceABC

from app.factories.services_factory_abc import ServicesFactoryABC

class ServicesFactory(ServicesFactoryABC):
    __slots__= (
        '__auth_service', 
        '__user_service'
        )

    def __init__(
            self,
            auth_service: AuthServiceABC,
            user_service: UserServiceABC,
            ) -> None:
        self.__auth_service: AuthServiceABC = auth_service
        self.__user_service: UserServiceABC = user_service


    async def get_auth_service(self) -> AuthServiceABC:
        return self.__auth_service
    
    async def get_user_service(self) -> UserServiceABC:
        return self.__user_service