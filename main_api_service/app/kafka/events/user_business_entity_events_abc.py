from abc import ABC, abstractmethod


class UserBusinessEntityEventsABC(ABC):

    @abstractmethod
    async def remove_user_business_entity(self, id: str, email_address: str, user_business_entity_name: str):
        ...
        
    @abstractmethod
    async def user_business_entity_removed(self, email_address: str, user_business_entity_name: str):
        ...