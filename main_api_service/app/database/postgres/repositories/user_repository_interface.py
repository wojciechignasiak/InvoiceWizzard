from typing import Protocol
from app.models.user_model import (
    CreateUserModel,
    UserPersonalInformationModel,
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )
from app.schema.schema import User

class IUserPostgresRepository(Protocol):

    async def create_user(self, new_user: CreateUserModel) -> User:
        ...

    async def get_user_by_id(self, user_id: str) -> User | None:
        ...

    async def get_user_by_email_address(self, user_email_adress: str) -> User | None:
        ...

    async def update_user_last_login(self, user_id: str) -> None:
        ...

    async def update_user_personal_information(self, user_id: str, personal_information: UserPersonalInformationModel) -> None:
        ...

    async def update_user_email_address(self, new_email: ConfirmedUserEmailChangeModel) -> None:
        ...

    async def update_user_password(self, new_password: ConfirmedUserPasswordChangeModel) -> None:
        ...

