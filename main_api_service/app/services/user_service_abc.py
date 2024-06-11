from abc import ABC, abstractmethod
from app.models.user_model import UserModel, RegisterUserModel

class UserServiceABC(ABC):

    @abstractmethod
    async def get_current_user(self, user_id: str) -> UserModel:
        pass

    @abstractmethod
    async def confirm_account(self, key_id: str) -> None:
        pass

    @abstractmethod
    async def register_account(self, new_user: RegisterUserModel, personal_salt: str, hashed_password: str):
        pass