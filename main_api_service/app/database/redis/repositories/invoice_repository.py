from app.database.redis.repositories.base_redis_repository import BaseRedisRepository
from app.custom_exceptions.custom_exceptions import DatabaseError

#3rd party libraries
from fastapi import status

#1st party libraries
from typing import Protocol
import json
import datetime

class IInvoiceRedisRepository(Protocol):

    async def initialize_invoice_removal(self, key_id: str, invoice_id: str) -> None:
        ...

    async def retrieve_invoice_removal(self, key_id: str) -> bytes:
        ...

    async def delete_invoice_removal(self, key_id: str) -> None:
        ...


async def new_invoice_redis_repository() -> IInvoiceRedisRepository:
    try:
        return InvoiceRedisRepository()
    except Exception as e:
        raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in while initializing new invoice redis repository.",
                class_and_method="new_invoice_redis_repository()",
                argument=None,
                child_error=e
            )


class InvoiceRedisRepository(BaseRedisRepository):

    async def initialize_invoice_removal(self, key_id: str, invoice_id: str) -> None:
        try:
            expiry_time = datetime.timedelta(days=2)
            is_invoice_removal_initialized: bool = await self.redis_client.set(
                name=f"remove_invoice:{key_id}", 
                value=json.dumps({"id":f"{invoice_id}"}),
                ex=expiry_time)
            
            if is_invoice_removal_initialized is False:
                raise DatabaseError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Can't initialize invoice removal")
            return is_invoice_removal_initialized
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
                message="Unexpected error occured in InvoiceRedisRepository while initializing invoice removal.",
                class_and_method="InvoiceRedisRepository.initialize_invoice_removal()",
                argument={'key_id': key_id, 'invoice_id': invoice_id},
                child_error=e
            )

    async def retrieve_invoice_removal(self, key_id: str) -> bytes:
        try:
            invoice_to_remove = await self.redis_client.get(f"remove_invoice:{key_id}")
            
            if invoice_to_remove is None:
                raise DatabaseError(status_code=status.HTTP_404_NOT_FOUND, message="Invoice not prepared for removal")
            return invoice_to_remove
        except DatabaseError as e:
            raise DatabaseError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="InvoiceRedisRepository.retrieve_invoice_removal()",
                argument={'key_id': key_id},
                child_error=e
            )
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in InvoiceRedisRepository while initializing retrieving invoice removal.",
                class_and_method="InvoiceRedisRepository.retrieve_invoice_removal()",
                argument={'key_id': key_id},
                child_error=e
            )

    async def delete_invoice_removal(self, key_id: str) -> None:
        try:
            await self.redis_client.delete(f"remove_invoice:{key_id}")
        except DatabaseError as e:
            raise DatabaseError(
                status_code=e.status_code,
                message=e.args[0],
                class_and_method="InvoiceRedisRepository.delete_invoice_removal()",
                argument={'key_id': key_id},
                child_error=e
            )
        except Exception as e:
            raise DatabaseError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occured in InvoiceRedisRepository while deleting invoice removal.",
                class_and_method="InvoiceRedisRepository.delete_invoice_removal()",
                argument={'key_id': key_id},
                child_error=e
            )