#internal modules
from main_api_service.app.schema.schema import Invoice, InvoiceItem
from main_api_service.app.models.invoice_model import CreateInvoiceModel, InvoiceModel, InvoiceItemModel
from main_api_service.app.models.user_business_entity_model import UserBusinessEntityModel
from main_api_service.app.models.external_business_entity_model import ExternalBusinessEntityModel
from main_api_service.app.models.invoice_item_model import CreateInvoiceItemModel
from main_api_service.app.database.redis.repositories.invoice_repository import IInvoiceRedisRepository, new_invoice_redis_repository
from main_api_service.app.database.postgres.repositories.invoice_repository import IInvoicePostgresRepository, new_invoice_postgres_repository
from main_api_service.app.kafka.events.invoice_events import IInvoiceEvents, new_invoice_events
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

class IExternalBusinessEntityService(Protocol):


    async def get_external_business_entity_by_id(self, user_id: UUID, invoice_id: UUID) -> ExternalBusinessEntityModel:
        ...

    async def get_multiple_external_business_entities_by_ids(self, user_id: UUID, invoices_ids: tuple[UUID, ...]) -> tuple[ExternalBusinessEntityModel]:
        ...

# async def new_invoice_service() -> IInvoiceService:
#     try:
#         return InvoiceService()
#     except Exception as e:
#         raise ServiceError(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             message="Unexpected error occurred in while creating invoice service",
#             argument=None,
#             child_error=e,
#         )