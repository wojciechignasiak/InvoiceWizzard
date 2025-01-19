#internal modules
from app.models.user_model import UserModel, CreateUserModel

#1st party libraries
from typing import Protocol

class IUserService(Protocol):

    async def get_user_by_id(self, user_id: str) -> UserModel:
        ...

    async def get_user_by_email_address(self, email_address: str) -> UserModel:
        ...

    async def get_user_registration_details_by_email_address(self, email_address: str) -> bytes:
        ...

    async def save_user_registration_data(self, key_id: str, new_user: CreateUserModel) -> None:
        ...

    async def send_user_registration_event(self, key_id: str, email_address: str) -> None:
        ...