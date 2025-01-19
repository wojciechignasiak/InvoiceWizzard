#internal modules
from app.models.user_model import RegisterUserModel

#1st party libraries
from typing import Protocol


class IRegisterAccountService(Protocol):

    async def register_user(self, register_user_model: RegisterUserModel) -> None:
        ...

    async def _check_is_email_arleady_taken(self, email_address: str) -> None:
        ...

    async def _check_is_email_arleady_registered(self, email_address: str) -> None:
        ...
