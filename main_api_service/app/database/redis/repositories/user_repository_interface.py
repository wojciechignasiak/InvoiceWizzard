from typing import Protocol
from app.models.user_model import (
    CreateUserModel,
    ConfirmedUserEmailChangeModel, 
    ConfirmedUserPasswordChangeModel
    )
from app.models.jwt_model import (
    JWTPayloadModel
)

class IUserRedisRepository(Protocol):

    async def save_user_registration_data(self, key_id: str, new_user: CreateUserModel) -> None:
        ...

    async def get_user_registration_data_by_id(self, key_id: str) -> bytes | None:
        ...

    async def get_user_registration_data_by_email_address(self, email_address: str) -> bytes | None:
        ...

    async def delete_user_registration_data_by_id(self, key_id: str) -> None:
        ...

    async def save_jwt_token(self, jwt_token: str, jwt_payload: JWTPayloadModel) -> None:
        ...

    async def get_jwt_token(self, jwt_token: str) -> bytes | None:
        ...

    async def delete_all_jwt_tokens_of_user(self, user_id: str) -> None:
        ...

    async def delete_jwt_token(self, token: str) -> None:
        ...

    async def save_new_email(self, key_id: str, new_email: ConfirmedUserEmailChangeModel) -> None:
        ...

    async def retrieve_new_email(self, key_id: str) -> bytes | None:
        ...

    async def delete_new_email(self, key_id: str) -> None:
        ...

    async def save_new_password(self, key_id: str, new_password: ConfirmedUserPasswordChangeModel) -> None:
        ...

    async def get_new_password(self, key_id: str) -> bytes | None:
        ...

    async def delete_new_password(self, key_id: str) -> None:
        ...