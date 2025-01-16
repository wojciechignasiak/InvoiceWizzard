
#internal modules
from app.models.user_model import UserModel

#3rd party libraries
from fastapi import Depends

#1st party libraries
from typing import Protocol

class IUserService(Protocol):

    async def get_user_by_id(self, user_id: str) -> UserModel:
        ...