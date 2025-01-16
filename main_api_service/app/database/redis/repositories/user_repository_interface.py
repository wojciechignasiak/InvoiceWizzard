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

    async def create_user(self, key_id: str, new_user: CreateUserModel) -> bool:
        ...

    async def search_user_by_id(self, key_id: str) -> bytes:
        ...

    async def is_user_arleady_registered(self, email_address: str) -> bool:
        ...

    async def delete_user_by_id(self, key_id: str) -> bool:
        ...

    async def save_jwt(self, jwt_token: str, jwt_payload: JWTPayloadModel) -> bool:
        ...

    async def retrieve_jwt(self, jwt_token: str) -> bytes | None:
        ...

    async def delete_all_jwt_tokens_of_user(self, user_id: str):
        ...

    async def delete_jwt_token(self, user_id: str, token: str):
        ...

    async def save_new_email(self, key_id: str, new_email: ConfirmedUserEmailChangeModel) -> bool:
        ...

    async def retrieve_new_email(self, key_id: str) -> bytes:
        ...

    async def delete_new_email(self, key_id: str):
        ...

    async def save_new_password(self, key_id: str, new_password: ConfirmedUserPasswordChangeModel) -> bool:
        ...

    async def retrieve_new_password(self, key_id: str) -> bytes:
        ...

    async def delete_new_password(self, key_id: str):
        ...