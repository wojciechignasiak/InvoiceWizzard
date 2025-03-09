#internal modules
from app.database.redis.repositories.invoice_repository import IInvoiceRedisRepository, new_invoice_redis_repository
from app.database.postgres.repositories.invoice_repository import IInvoicePostgresRepository, new_invoice_postgres_repository
from app.custom_exceptions.custom_exceptions import (
    ServiceError,
    DatabaseError,
    LogicError,
)

#3rd party libraries
from fastapi import Depends, status

#1st party libraries
from typing import Protocol
import os
import re
import datetime


class IInvoiceService(Protocol):
    ...

async def new_invoice_service() -> IInvoiceService:
    try:
        return InvoiceService()
    except Exception as e:
        pass

class InvoiceService:

    __slots__ = ('invoice_postgres_repository', 'invoice_redis_repository', 'invoice_events',)

    def __init__(
        self,
        invoice_postgres_repository: IInvoicePostgresRepository = Depends(new_invoice_postgres_repository),
        invoice_redis_repository: IInvoiceRedisRepository = Depends(new_invoice_redis_repository),
        invoice_events = 'a'
    ):
        self._invoice_postgres_repository: IInvoicePostgresRepository = invoice_postgres_repository
        self._invoice_redis_repository: IInvoiceRedisRepository = invoice_redis_repository
        self._invoice_events = invoice_events