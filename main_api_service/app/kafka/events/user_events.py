#internal modules
from main_api_service.app.models.kafka_topics_enum import KafkaTopicsEnum
from main_api_service.app.kafka.events.kafka_producer_base import KafkaProducerBase
from main_api_service.app.custom_exceptions.custom_exceptions import EventError

#3rd party modules
from fastapi import status

#1st party modules
from typing import Protocol
import json
from uuid import UUID


class IUserEvents(Protocol):

    async def account_registered(self, key_id: UUID, email_address: str) -> None:
        ...

    async def account_confirmed(self, email_address: str) -> None:
        ...

    async def change_email(self, key_id: UUID, email_address: str) -> None:
        ...

    async def email_changed(self, email_address: str) -> None:
        ...

    async def change_password(self, key_id: UUID, email_address: str) -> None:
        ...

    async def reset_password(self, key_id: UUID, email_address: str) -> None:
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
                argument=None,
                child_error=e,
            )

class UserEvents(KafkaProducerBase, IUserEvents):

    async def account_registered(self, key_id: UUID, email_address: str) -> None:
        try:
            message = {
                "id": key_id, 
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
                argument={'key_id': key_id, 'email_address': email_address},
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
                argument={'email_address': email_address},
                child_error=e,
            )

    async def change_email(self, key_id: UUID, email_address: str) -> None:
        try:
            message = {
                "id": key_id,
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
                argument={'key_id': key_id, 'email_address': email_address},
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
                argument={'email_address': email_address},
                child_error=e,
            )

    async def change_password(self, key_id: UUID, email_address: str) -> None:
        try:
            message = {
                "id": key_id,
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
                argument={'key_id': key_id, 'email_address': email_address},
                child_error=e,
            )

    async def reset_password(self, key_id: UUID, email_address: str) -> None:
        try:
            message = {
                "id": key_id,
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
                argument={'key_id': key_id, 'email_address': email_address},
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
                argument={'email_address': email_address},
                child_error=e,
            )