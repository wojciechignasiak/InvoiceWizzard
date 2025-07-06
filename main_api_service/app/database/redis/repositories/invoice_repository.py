from main_api_service.app.database.redis.repositories.base_redis_repository import BaseRedisRepository
from main_api_service.app.custom_exceptions.custom_exceptions import DatabaseError

#3rd party libraries
from fastapi import status

#1st party libraries
from typing import Protocol
import json
import datetime
from uuid import UUID

class IInvoiceRedisRepository(Protocol):

    async def initialize_invoice_removal(self, key_id: UUID, invoice_id: UUID) -> None:
        ...

    async def get_invoice_removal(self, key_id: UUID) -> bytes | None:
        ...

    async def delete_invoice_removal(self, key_id: UUID) -> None:
        ...


async def new_invoice_redis_repository() -> IInvoiceRedisRepository:
    try:
        return InvoiceRedisRepository()
    except Exception as e:
        raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred while initializing new invoice redis repository.",
                class_and_method="new_invoice_redis_repository()",
                argument=None,
                child_error=e
            )

class InvoiceRedisRepository(BaseRedisRepository, IInvoiceRedisRepository):

    async def initialize_invoice_removal(self, key_id: UUID, invoice_id: UUID) -> None:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_invoice_removal_initialized: bool = await self.redis_client.set(
                name=f"remove_invoice:{key_id}", 
                value=json.dumps({"invoice_id":f"{invoice_id}"}),
                ex=expiry_time)
            
            if not is_invoice_removal_initialized:
                raise DatabaseError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Can't initialize invoice removal")
        except DatabaseError as e:
            raise DatabaseError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="InvoiceRedisRepository.initialize_invoice_removal()",
                argument={'key_id': key_id, 'invoice_id': invoice_id},
                child_error=e
            )
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceRedisRepository while initializing invoice removal.",
                class_and_method="InvoiceRedisRepository.initialize_invoice_removal()",
                argument={'key_id': key_id, 'invoice_id': invoice_id},
                child_error=e
            )

    async def get_invoice_removal(self, key_id: UUID) -> bytes | None:
        try:
            invoice_to_remove: bytes | None = await self.redis_client.get(f"remove_invoice:{key_id}")
            return invoice_to_remove
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceRedisRepository while retrieving invoice removal.",
                class_and_method="InvoiceRedisRepository.retrieve_invoice_removal()",
                argument={'key_id': key_id},
                child_error=e
            )

    async def delete_invoice_removal(self, key_id: UUID) -> None:
        try:
            await self.redis_client.delete(f"remove_invoice:{key_id}")
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceRedisRepository while deleting invoice removal.",
                class_and_method="InvoiceRedisRepository.delete_invoice_removal()",
                argument={'key_id': key_id},
                child_error=e
            )