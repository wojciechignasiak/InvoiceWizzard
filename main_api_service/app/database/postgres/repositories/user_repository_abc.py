from abc import ABC, abstractmethod
from app.models.user_model import (
    CreateUserModel,
    UserPersonalInformationModel,
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )
from app.schema.schema import User

class UserPostgresRepositoryABC(ABC):
    @abstractmethod
    async def create_user(self, new_user: CreateUserModel) -> User:
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User:
        ...

    @abstractmethod
    async def get_user_by_email_address(self, user_email_adress: str) -> User:
        ...

    @abstractmethod
    async def is_email_address_arleady_taken(self, user_email_adress: str) -> bool:
        ...
    
    @abstractmethod
    async def update_user_last_login(self, user_id: str) -> User:
        ...

    @abstractmethod
    async def update_user_personal_information(self, user_id: str, personal_information: UserPersonalInformationModel) -> User:
        ...
    
    @abstractmethod
    async def update_user_email_address(self, new_email: ConfirmedUserEmailChangeModel) -> User:
        ...

    @abstractmethod
    async def update_user_password(self, new_password: ConfirmedUserPasswordChangeModel) -> User:
        ...

