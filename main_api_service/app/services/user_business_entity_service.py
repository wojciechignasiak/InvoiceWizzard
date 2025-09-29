#internal modules
from main_api_service.app.schema.schema import Invoice, InvoiceItem
from main_api_service.app.models.invoice_model import CreateInvoiceModel, InvoiceModel, InvoiceItemModel
from main_api_service.app.models.user_business_entity_model import UserBusinessEntityModel
from main_api_service.app.models.external_business_entity_model import ExternalBusinessEntityModel
from main_api_service.app.models.invoice_item_model import CreateInvoiceItemModel
from main_api_service.app.database.redis.repositories.invoice_repository import IInvoiceRedisRepository, new_invoice_redis_repository
from main_api_service.app.database.postgres.repositories.invoice_repository import IInvoicePostgresRepository, new_invoice_postgres_repository
from main_api_service.app.kafka.events.invoice_events import IInvoiceEvents, new_invoice_events
from main_api_service.app.database.postgres.repositories.user_business_entity_repository import IUserBusinessEntityPostgresRepository, new_user_business_entity_postgres_repository
from main_api_service.app.custom_exceptions.custom_exceptions import (
    ServiceError,
    DatabaseError,
    LogicError,
    EventError, DataNotFoundError
)

#3rd party libraries
from fastapi import Depends, status

#1st party libraries
from typing import Protocol
import os
import re
import datetime
from uuid import UUID

class IUserBusinessEntityService(Protocol):

    async def get_user_business_entity_by_id(self, user_id: UUID, user_business_entity_id: UUID) -> UserBusinessEntityModel:
        ...

    async def get_multiple_user_business_entities_by_ids(self, user_id: UUID, user_business_entities_by_ids: tuple[UUID, ...]) -> tuple[UserBusinessEntityModel, ...]:
        ...

def new_user_business_entity_service(
    user_business_entity_repository: IUserBusinessEntityPostgresRepository = Depends(new_user_business_entity_postgres_repository),
) -> IUserBusinessEntityService:
    try:
        return UserBusinessEntityService(
            user_business_entity_repository
        )
    except Exception as e:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error occurred in while creating user business entity service",
            argument=None,
            child_error=e,
        )

class UserBusinessEntityService(IUserBusinessEntityService):
    def __init__(
            self,
            user_business_entity_repository: IUserBusinessEntityPostgresRepository,
    ):
        self._user_business_entity_repository: IUserBusinessEntityPostgresRepository = user_business_entity_repository

    async def get_user_business_entity_by_id(self, user_id: UUID, user_business_entity_id: UUID) -> UserBusinessEntityModel:
        try:
            user_business_entity: UserBusinessEntity | None = self._user_business_entity_repository.get_user_business_entity_by_id(user_id, user_business_entity_id)
            if not user_business_entity:
                raise DataNotFoundError(
                    message="User business entity not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            pass

    async def get_multiple_user_business_entities_by_ids(self, user_id: UUID, user_business_entities_by_ids: tuple[UUID, ...]) -> tuple[UserBusinessEntityModel, ...]:
        try:
            pass
        except Exception as e:
            pass