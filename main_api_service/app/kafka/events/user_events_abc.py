from abc import ABC, abstractmethod


class UserEventsABC(ABC):

    @abstractmethod
    async def account_registered_event(self, id: str, email_address: str):
        ...
    @abstractmethod
    async def account_confirmed_event(self, email_address: str):
        ...
    @abstractmethod
    async def change_email_event(self, id: str, email_address: str):
        ...
    @abstractmethod
    async def email_changed_event(self, email_address: str):
        ...
    @abstractmethod
    async def change_password_event(self, id: str, email_address: str):
        ...
    @abstractmethod
    async def reset_password_event(self, id: str, email_address: str):
        ...
    @abstractmethod
    async def password_changed_event(self, email_address: str):
        ...