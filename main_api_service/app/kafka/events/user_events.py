#internal modules
from app.models.kafka_topics_enum import KafkaTopicsEnum
from app.kafka.events.kafka_producer_base import KafkaProducerBase
from app.custom_exceptions.custom_exceptions import EventError

#3rd party modules
from fastapi import status

#1st party modules
from typing import Protocol
import json


class IUserEvents(Protocol):

    async def account_registered(self, id: str, email_address: str) -> None:
        ...

    async def account_confirmed(self, email_address: str) -> None:
        ...

    async def change_email(self, id: str, email_address: str) -> None:
        ...

    async def email_changed(self, email_address: str) -> None:
        ...

    async def change_password(self, id: str, email_address: str) -> None:
        ...

    async def reset_password(self, id: str, email_address: str) -> None:
        ...

    async def password_changed(self, email_address: str) -> None:
        ...

async def new_user_events() -> IUserEvents:
    try:
        return UserEvents()
    except Exception as e:
        raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while creating user events class instance",
                class_and_method="new_user_events()",
                argument=None,
                child_error=e,
            )

class UserEvents(KafkaProducerBase):

    async def account_registered(self, id: str, email_address: str) -> None:
        try:
            message = {
                "id": id, 
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.account_registered.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserEvents while creating account registered event",
                class_and_method="UserEvents.account_registered()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )

    async def account_confirmed(self, email_address: str) -> None:
        try:
            message = {
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.account_confirmed.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserEvents while creating account confirmed event",
                class_and_method="UserEvents.account_confirmed()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )

    async def change_email(self, id: str, email_address: str) -> None:
        try:
            message = {
                "id": id,
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.change_email.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserEvents while creating change email event",
                class_and_method="UserEvents.change_email()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )

    async def email_changed(self, email_address: str) -> None:
        try:
            message = {
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.email_changed.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserEvents while creating email changed event",
                class_and_method="UserEvents.email_changed()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )

    async def change_password(self, id: str, email_address: str) -> None:
        try:
            message = {
                "id": id,
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.change_password.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserEvents while creating change password event",
                class_and_method="UserEvents.change_password()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )

    async def reset_password(self, id: str, email_address: str) -> None:
        try:
            message = {
                "id": id,
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.reset_password.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserEvents while creating reset password event",
                class_and_method="UserEvents.reset_password()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )

    async def password_changed(self, email_address: str) -> None:
        try:
            message = {
                "email": email_address
            }
            await self.kafka_producer.send(
                KafkaTopicsEnum.password_changed.value, 
                json.dumps(message).encode('utf-8')
                )
        except Exception as e:
            raise EventError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserEvents while creating password changed event",
                class_and_method="UserEvents.password_changed()",
                argument={'id': id, 'email_address': email_address},
                child_error=e,
            )