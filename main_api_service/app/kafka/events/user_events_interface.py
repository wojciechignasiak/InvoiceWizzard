from typing import Protocol


class IUserEvents(Protocol):

    async def account_registered_event(self, id: str, email_address: str):
        ...

    async def account_confirmed_event(self, email_address: str):
        ...

    async def change_email_event(self, id: str, email_address: str):
        ...

    async def email_changed_event(self, email_address: str):
        ...

    async def change_password_event(self, id: str, email_address: str):
        ...

    async def reset_password_event(self, id: str, email_address: str):
        ...

    async def password_changed_event(self, email_address: str):
        ...