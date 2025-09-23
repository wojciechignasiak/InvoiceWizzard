#internal modules
from main_api_service.app.storage.file_format_converter import IFileFormatConverter
from main_api_service.app.models.user_business_entity_model import UserBusinessEntityModel
from main_api_service.app.models.external_business_entity_model import ExternalBusinessEntityModel
from main_api_service.app.schema.schema import Invoice, InvoiceItem
from main_api_service.app.models.invoice_model import CreateInvoiceModel, InvoiceModel, InvoiceItemModel, UpdateInvoiceModel
from main_api_service.app.services.user_business_entity_service import IUserBusinessEntityService
from main_api_service.app.services.external_business_entity_service import IExternalBusinessEntityService
from main_api_service.app.database.redis.repositories.invoice_repository import IInvoiceRedisRepository, new_invoice_redis_repository
from main_api_service.app.database.postgres.repositories.invoice_repository import IInvoicePostgresRepository, new_invoice_postgres_repository
from main_api_service.app.kafka.events.invoice_events import IInvoiceEvents, new_invoice_events
from main_api_service.app.storage.io_storage import IIOStorage, get_io_storage
from main_api_service.app.documents.file_builder import IFileBuilder
from main_api_service.app.custom_exceptions.custom_exceptions import (
    ServiceError,
    DatabaseError,
    LogicError,
    EventError,
    DataNotFoundError,
    StorageError
)

#3rd party libraries
from fastapi import Depends, status

#1st party libraries
from typing import Protocol
from datetime import date
from pathlib import Path
import uuid
import ast


class IInvoiceService(Protocol):

    async def create_invoice(self, user_id: uuid.UUID, new_invoice: CreateInvoiceModel) -> uuid.UUID:
        ...

    async def get_invoice_by_id(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> InvoiceModel:
        ...

    async def get_all_invoices(
            self,
            user_id: uuid.UUID,
            page: int,
            items_per_page: int,
            user_business_entity_id: uuid.UUID | None,
            user_business_entity_name: str | None,
            external_business_entity_id: uuid.UUID | None,
            external_business_entity_name: str | None,
            invoice_number: str | None,
            start_issue_date: date | None,
            end_issue_date: date | None,
            start_sale_date: date | None,
            end_sale_date: date | None,
            payment_method: str | None,
            start_payment_deadline: date | None,
            end_payment_deadline: date | None,
            start_added_date: date | None,
            end_added_date: date | None,
            is_settled: bool | None,
            is_issued: bool | None,
            in_trash: bool | None,
    ) -> list[InvoiceModel]:
        ...

    async def update_invoice(self, user_id: uuid.UUID, update_invoice: UpdateInvoiceModel) -> None:
        ...

    async def update_invoice_in_trash_status(self, user_id: uuid.UUID, invoice_id: uuid.UUID, in_trash: bool) -> None:
        ...

    async def initialize_invoice_removal(self, user_id: uuid.UUID, user_email: str, invoice_id: uuid.UUID) -> None:
        ...

    async def confirm_invoice_removal(self, removal_key_id: uuid.UUID, user_id: uuid.UUID, user_email: str) -> None:
        ...

    async def add_file_to_invoice(self, user_id: uuid.UUID, invoice_id: uuid.UUID, invoice_file: bytes,
                                  invoice_file_extension: str) -> None:
        ...

    async def delete_file_from_invoice(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> None:
        ...

    async def get_invoice_file(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> Path:
        ...

    async def generate_invoice_file(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> None:
        ...

def new_invoice_service() -> IInvoiceService:
    try:
        return InvoiceService()
    except Exception as e:
        raise ServiceError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Unexpected error occurred in while creating invoice service",
            argument=None,
            child_error=e,
        )

class InvoiceService(IInvoiceService):

    __slots__ = (
        'invoice_postgres_repository',
        'invoice_redis_repository',
        'invoice_events',
        'user_business_entity_service',
        'external_business_entity_service',
        'io_storage',
        'file_format_converter',
        'file_builder',
    )

    def __init__(
        self,
        invoice_postgres_repository: IInvoicePostgresRepository = Depends(new_invoice_postgres_repository),
        invoice_redis_repository: IInvoiceRedisRepository = Depends(new_invoice_redis_repository),
        invoice_events: IInvoiceEvents = Depends(new_invoice_events),
        user_business_entity_service: IUserBusinessEntityService = None,
        external_business_entity_service: IExternalBusinessEntityService = None,
        io_storage: IIOStorage = Depends(get_io_storage),
        file_format_converter: IFileFormatConverter = None,
        file_builder: IFileBuilder = None,
    ):
        self._invoice_postgres_repository: IInvoicePostgresRepository = invoice_postgres_repository
        self._invoice_redis_repository: IInvoiceRedisRepository = invoice_redis_repository
        self._invoice_events: IInvoiceEvents = invoice_events
        self._user_business_entity_service: IUserBusinessEntityService = user_business_entity_service
        self._external_business_entity_service: IExternalBusinessEntityService = external_business_entity_service
        self._io_storage: IIOStorage = io_storage
        self._file_format_converter: IFileFormatConverter = file_format_converter
        self._file_builder: IFileBuilder = file_builder

    async def create_invoice(self, user_id: uuid.UUID, new_invoice: CreateInvoiceModel) -> uuid.UUID:
        try:
            invoices: tuple[Invoice] | tuple = await  self._invoice_postgres_repository.get_invoice_by_invoice_number(user_id, new_invoice.invoice_number)
            if invoices:
                invoice: Invoice | None = self._check_is_invoice_unique(invoices, new_invoice.invoice_number, new_invoice.user_business_entity_id, new_invoice.external_business_entity_id)
                if invoice:
                    if invoice.in_trash:
                        raise LogicError(message=f"Invoice number {new_invoice.invoice_number} already exists but is in trash", status_code=status.HTTP_409_CONFLICT)
                    else:
                        raise LogicError(message=f"Invoice number {new_invoice.invoice_number} already exists", status_code=status.HTTP_409_CONFLICT)

            invoice_id: uuid.UUID = uuid.uuid4()
            await self._invoice_postgres_repository.create_invoice(invoice_id, user_id, new_invoice,)
            for invoice_item in new_invoice.invoice_items:
                invoice_item_id: uuid.UUID = uuid.uuid4()
                await self._invoice_postgres_repository.create_invoice_item(user_id, invoice_id, invoice_item_id, invoice_item)
            return invoice_id
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'new_invoice': new_invoice},
                child_error=e,
            )
        except ServiceError as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'new_invoice': new_invoice},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while creating invoice",
                argument={'user_id': user_id, 'new_invoice': new_invoice},
                child_error=e,
            )

    async def get_invoice_by_id(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> InvoiceModel:
        try:
            invoice: Invoice | None = await self._invoice_postgres_repository.get_invoice_by_id(user_id, invoice_id)
            if not invoice:
                raise DataNotFoundError(status_code=status.HTTP_404_NOT_FOUND, message=f"Invoice with id: {invoice_id} not found")
            user_business_entity: UserBusinessEntityModel = await self._user_business_entity_service.get_user_business_entity_by_id(
                user_id, invoice.user_business_entity_id)
            external_business_entity: ExternalBusinessEntityModel = await self._external_business_entity_service.get_external_business_entity_by_id(
                user_id, invoice.external_business_entity_id)
            invoice_items: tuple[InvoiceItem] | tuple = await self._invoice_postgres_repository.get_invoice_items_by_invoice_id(user_id, invoice_id, in_trash=False)
            if invoice_items:
                invoice_items_models: list[InvoiceItemModel] = [await self._convert_invoice_item_schema_to_invoice_item_model(invoice_item) for invoice_item in invoice_items if invoice_item.in_trash == False]
                invoice_gross_value: float = self._calculate_invoice_gross_value(invoice_items_models)
                invoice_net_value: float = self._calculate_invoice_net_value(invoice_items_models)
                invoice_model: InvoiceModel = self._convert_invoice_schema_to_invoice_model(invoice, user_business_entity, external_business_entity, invoice_items_models, invoice_gross_value, invoice_net_value)
            else:
                invoice_model: InvoiceModel = self._convert_invoice_schema_to_invoice_model(invoice, user_business_entity, external_business_entity, None, None, None)
            return invoice_model
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id},
                child_error=e,
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while getting invoice",
                argument={'user_id': user_id, 'invoice_id': invoice_id},
                child_error=e,
            )

    async def get_all_invoices(
            self,
            user_id: uuid.UUID,
            page: int,
            items_per_page: int,
            user_business_entity_id: uuid.UUID | None,
            user_business_entity_name: str | None,
            external_business_entity_id: uuid.UUID | None,
            external_business_entity_name: str | None,
            invoice_number: str | None,
            start_issue_date: date | None,
            end_issue_date: date | None,
            start_sale_date: date | None,
            end_sale_date: date | None,
            payment_method: str | None,
            start_payment_deadline: date | None,
            end_payment_deadline: date | None,
            start_added_date: date | None,
            end_added_date: date | None,
            is_settled: bool | None,
            is_issued: bool | None,
            in_trash: bool | None,
    ) -> list[InvoiceModel]:
        try:
            invoices: tuple[Invoice] | tuple = await self._invoice_postgres_repository.get_all_invoices(
                user_id,
                page,
                items_per_page,
                user_business_entity_id,
                user_business_entity_name,
                external_business_entity_id,
                external_business_entity_name,
                invoice_number,
                start_issue_date,
                end_issue_date,
                start_sale_date,
                end_sale_date,
                payment_method,
                start_payment_deadline,
                end_payment_deadline,
                start_added_date,
                end_added_date,
                is_settled,
                is_issued,
                in_trash,
            )
            if not invoices:
                raise DataNotFoundError(message="Invoices not found", status_code=status.HTTP_404_NOT_FOUND)

            invoices_items: tuple[InvoiceItem] | tuple = await self._invoice_postgres_repository.get_invoice_items_for_multiple_invoices_by_invoice_id(user_id, tuple(invoice.id for invoice in invoices), in_trash)
            user_business_entities: tuple[UserBusinessEntityModel] = await self._user_business_entity_service.get_multiple_user_business_entities_by_ids(user_id, tuple(invoice.user_business_entity_id for invoice in invoices))
            external_business_entities: tuple[ExternalBusinessEntityModel] = await self._external_business_entity_service.get_multiple_external_business_entities_by_ids(user_id, tuple(invoice.external_business_entity_id for invoice in invoices))

            invoices_items_models: list[InvoiceItemModel] = [
                await self._convert_invoice_item_schema_to_invoice_item_model(invoice_item) for invoice_item in
                invoices_items if invoice_item.in_trash == False]

            invoice_models: list[InvoiceModel] = []
            for invoice in invoices:
                user_business_entity_model: UserBusinessEntityModel = next(user_business_entity for user_business_entity in user_business_entities if user_business_entity.id == invoice.user_business_entity_id)
                external_business_entity_model: ExternalBusinessEntityModel = next(external_business_entity for external_business_entity in external_business_entities if external_business_entity.id == invoice.external_business_entity_id)
                invoice_items_models: list[InvoiceItemModel] | None = [invoice_item_model for invoice_item_model in invoices_items_models if invoice_item_model.invoice_id == invoice.id] or None
                if invoice_items_models:
                    invoice_gross_value: float = self._calculate_invoice_gross_value(invoice_items_models)
                    invoice_net_value: float = self._calculate_invoice_net_value(invoice_items_models)
                    invoice_model: InvoiceModel = self._convert_invoice_schema_to_invoice_model(
                            invoice,
                            user_business_entity_model,
                            external_business_entity_model,
                            invoice_items_models,
                            invoice_gross_value,
                            invoice_net_value,
                        )
                    invoice_models.append(invoice_model)

            return invoice_models
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={
                    'user_id': user_id,
                    'page': page,
                    'items_per_page': items_per_page,
                    'user_business_entity_id': user_business_entity_id,
                    'user_business_entity_name': user_business_entity_name,
                    'external_business_entity_id': external_business_entity_id,
                    'external_business_entity_name': external_business_entity_name,
                    'invoice_number': invoice_number,
                    'start_issue_date': start_issue_date,
                    'end_issue_date': end_issue_date,
                    'start_sale_date': start_sale_date,
                    'end_sale_date': end_sale_date,
                    'payment_method': payment_method,
                    'start_payment_deadline': start_payment_deadline,
                    'end_payment_deadline': end_payment_deadline,
                    'start_added_date': start_added_date,
                    'end_added_date': end_added_date,
                    'is_settled': is_settled,
                    'is_issued': is_issued,
                    'in_trash': in_trash
                },
                child_error=e,
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={
                    'user_id': user_id,
                    'page': page,
                    'items_per_page': items_per_page,
                    'user_business_entity_id': user_business_entity_id,
                    'user_business_entity_name': user_business_entity_name,
                    'external_business_entity_id': external_business_entity_id,
                    'external_business_entity_name': external_business_entity_name,
                    'invoice_number': invoice_number,
                    'start_issue_date': start_issue_date,
                    'end_issue_date': end_issue_date,
                    'start_sale_date': start_sale_date,
                    'end_sale_date': end_sale_date,
                    'payment_method': payment_method,
                    'start_payment_deadline': start_payment_deadline,
                    'end_payment_deadline': end_payment_deadline,
                    'start_added_date': start_added_date,
                    'end_added_date': end_added_date,
                    'is_settled': is_settled,
                    'is_issued': is_issued,
                    'in_trash': in_trash
                },
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while getting invoice",
                argument={
                    'user_id': user_id,
                    'page': page,
                    'items_per_page': items_per_page,
                    'user_business_entity_id': user_business_entity_id,
                    'user_business_entity_name': user_business_entity_name,
                    'external_business_entity_id': external_business_entity_id,
                    'external_business_entity_name': external_business_entity_name,
                    'invoice_number': invoice_number,
                    'start_issue_date': start_issue_date,
                    'end_issue_date': end_issue_date,
                    'start_sale_date': start_sale_date,
                    'end_sale_date': end_sale_date,
                    'payment_method': payment_method,
                    'start_payment_deadline': start_payment_deadline,
                    'end_payment_deadline': end_payment_deadline,
                    'start_added_date': start_added_date,
                    'end_added_date': end_added_date,
                    'is_settled': is_settled,
                    'is_issued': is_issued,
                    'in_trash': in_trash
                },
                child_error=e,
            )

    async def update_invoice(self, user_id: uuid.UUID, update_invoice: UpdateInvoiceModel) -> None:
        try:
            await self.get_invoice_by_id(user_id, update_invoice.id)
            invoices: tuple[Invoice] | tuple = await  self._invoice_postgres_repository.get_invoice_by_invoice_number(
                user_id, update_invoice.invoice_number)
            invoices: tuple[Invoice] | tuple = tuple(invoice for invoice in invoices if invoice.id != update_invoice.id)
            if invoices:
                invoice: Invoice | None = self._check_is_invoice_unique(invoices, update_invoice.invoice_number, update_invoice.user_business_entity_id, update_invoice.external_business_entity_id)
                if invoice:
                    raise LogicError(message="Invoice with provided business, number and type already exists beside one to update.", status_code=status.HTTP_409_CONFLICT)
            await self._invoice_postgres_repository.update_invoice(user_id, update_invoice)
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'update_invoice': update_invoice},
                child_error=e,
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'update_invoice': update_invoice},
                child_error=e,
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'update_invoice': update_invoice},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while updating invoice",
                argument={'user_id': user_id, 'update_invoice': update_invoice},
                child_error=e,
            )

    async def update_invoice_in_trash_status(self, user_id: uuid.UUID, invoice_id: uuid.UUID, in_trash: bool) -> None:
        try:
            invoice: InvoiceModel = await self.get_invoice_by_id(user_id, invoice_id)
            await self._invoice_postgres_repository.update_invoice_in_trash_status(user_id, invoice_id, in_trash)
            if invoice.invoice_items:
                await self._invoice_postgres_repository.update_invoice_items_in_trash_status(user_id, invoice_id, in_trash)
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'in_trash': in_trash},
                child_error=e,
            )
        except (ServiceError, DatabaseError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'in_trash': in_trash},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while changing invoice in trash status",
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'in_trash': in_trash},
                child_error=e,
            )

    async def initialize_invoice_removal(self, user_id: uuid.UUID, user_email: str, invoice_id: uuid.UUID) -> None:
        try:
            invoice: InvoiceModel = await self.get_invoice_by_id(user_id, invoice_id)
            removal_key_id: uuid.UUID = uuid.uuid4()
            await self._invoice_redis_repository.initialize_invoice_removal(removal_key_id, invoice_id)
            await self._invoice_events.remove_invoice(
                removal_key_id,
                user_email,
                invoice.invoice_number,
                invoice.user_business_entity.company_name,
                invoice.external_business_entity.company_name,
                invoice.is_issued,
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'user_email': user_email, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except (ServiceError, DatabaseError, EventError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'user_email': user_email, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while initializing invoice removal",
                argument={'user_id': user_id, 'user_email': user_email, 'invoice_id': invoice_id,},
                child_error=e,
            )

    async def confirm_invoice_removal(self, removal_key_id: uuid.UUID, user_id: uuid.UUID, user_email: str) -> None:
        try:
            invoice_removal: bytes | None = await self._invoice_redis_repository.get_invoice_removal(removal_key_id)
            if not invoice_removal:
                raise DataNotFoundError(
                    message="Invoice removal process not initialized or expired", status_code=status.HTTP_404_NOT_FOUND,
                )
            invoice_removal: dict[str, uuid.UUID] = self._convert_invoice_removal_bytes_to_dict(invoice_removal)
            invoice: InvoiceModel = await self.get_invoice_by_id(user_id, invoice_removal['invoice_id'])
            if invoice.invoice_pdf:
                await self._io_storage.remove_invoice_file(user_id, invoice.id)
            await self._invoice_redis_repository.delete_invoice_removal(removal_key_id)
            await self._invoice_events.invoice_removed(
                uuid.uuid4(),
                user_email,
                invoice.invoice_number,
                invoice.user_business_entity.company_name,
                invoice.external_business_entity.company_name,
                invoice.is_issued,
            )

        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'removal_key_id': removal_key_id, 'user_id': user_id, 'user_email': user_email,},
                child_error=e,
            )
        except (ServiceError, DatabaseError, EventError, StorageError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'removal_key_id': removal_key_id, 'user_id': user_id, 'user_email': user_email,},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while removing invoice",
                argument={'removal_key_id': removal_key_id, 'user_id': user_id, 'user_email': user_email,},
                child_error=e,
            )

    async def add_file_to_invoice(self, user_id: uuid.UUID, invoice_id: uuid.UUID, invoice_file: bytes, invoice_file_extension: str) -> None:
        try:
            invoice: InvoiceModel = await self.get_invoice_by_id(user_id, invoice_id)
            if invoice.invoice_pdf:
                raise LogicError(message="Invoice already have pdf file. Delete current file first", status_code=status.HTTP_409_CONFLICT)

            match invoice_file_extension:
                case "pdf":
                    await self._io_storage.save_invoice_file(user_id, invoice_id, invoice_file)
                case "jpg" | "jpeg" | "png":
                    converted_invoice_file: bytes = await  self._file_format_converter.convert_file_format(invoice_file)
                    await self._io_storage.save_invoice_file(user_id, invoice_id, converted_invoice_file)
                case _:
                    raise LogicError(message="Unsupported invoice file format. Supported file formats are: pdf, jpg, jpeg, png", status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
            await self._invoice_postgres_repository.update_invoice_file_status(user_id, invoice_id, True)
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'invoice_file': invoice_file,},
                child_error=e,
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'invoice_file': invoice_file,},
                child_error=e,
            )
        except (ServiceError, DatabaseError, EventError, StorageError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'invoice_file': invoice_file,},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while adding file to invoice",
                argument={'user_id': user_id, 'invoice_id': invoice_id, 'invoice_file': invoice_file,},
                child_error=e,
            )

    async def delete_file_from_invoice(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> None:
        try:
            invoice: InvoiceModel = await self.get_invoice_by_id(user_id, invoice_id)
            if not invoice.invoice_pdf:
                raise LogicError(message="Invoice don't have file", status_code=status.HTTP_409_CONFLICT)
            await self._io_storage.remove_invoice_file(user_id, invoice_id)
            await self._invoice_postgres_repository.update_invoice_file_status(user_id, invoice_id, False)
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except (ServiceError, DatabaseError, EventError, StorageError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while deleting file from invoice",
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )

    async def get_invoice_file(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> Path:
        try:
            invoice: InvoiceModel = await self.get_invoice_by_id(user_id, invoice_id)
            if not invoice.invoice_pdf:
                raise LogicError(message="Invoice don't have file", status_code=status.HTTP_409_CONFLICT)
            file: Path | None = await self._io_storage.get_invoice_file(user_id, invoice_id)
            if not file:
                raise DataNotFoundError(message="Invoice file not found", status_code=status.HTTP_404_NOT_FOUND)
            return file
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except (ServiceError, DatabaseError, EventError, StorageError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while deleting file from invoice",
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )

    async def generate_invoice_file(self, user_id: uuid.UUID, invoice_id: uuid.UUID) -> None:
        try:
            invoice: InvoiceModel = await self.get_invoice_by_id(user_id, invoice_id)
            if invoice.invoice_pdf:
                raise LogicError(message="Invoice already have file", status_code=status.HTTP_409_CONFLICT)
            invoice_html: str = await self._file_builder.build_invoice_file(invoice)
            converted_invoice_file: bytes = await self._file_format_converter.convert_file_format(invoice_html)
            await self._io_storage.save_invoice_file(user_id, invoice_id, converted_invoice_file)
            await self._invoice_postgres_repository.update_invoice_file_status(user_id, invoice_id, True)
        except LogicError as e:
            raise LogicError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except DataNotFoundError as e:
            raise DataNotFoundError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except (ServiceError, DatabaseError, EventError, StorageError) as e:
            raise ServiceError(
                status_code=e.status_code,
                message=e.message,
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while deleting file from invoice",
                argument={'user_id': user_id, 'invoice_id': invoice_id,},
                child_error=e,
            )

    @staticmethod
    def _check_is_invoice_unique(invoices: tuple[Invoice], invoice_number: str, user_business_entity_id: uuid.UUID, external_business_entity_id: uuid.UUID) -> Invoice | None:
        try:
            for invoice in invoices:
                if (
                        invoice.invoice_number == invoice_number and
                        invoice.user_business_entity_id == user_business_entity_id and
                        invoice.external_business_entity_id == external_business_entity_id
                ):
                    return invoice
                else:
                    return None
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while checking if invoice is unique",
                argument={'invoices': invoices, 'invoice_number': invoice_number, 'user_business_entity_id': user_business_entity_id, 'external_business_entity_id': external_business_entity_id},
                child_error=e,
            )

    @staticmethod
    def _calculate_invoice_gross_value(invoice_items: list[InvoiceItemModel]) -> float:
        try:
            return sum(invoice_item.gross_value for invoice_item in invoice_items)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserService while calculating invoice gross value",
                argument={'invoice_items': invoice_items},
                child_error=e,
            )

    @staticmethod
    def _calculate_invoice_net_value(invoice_items: list[InvoiceItemModel]) -> float:
        try:
            return sum(invoice_item.net_value for invoice_item in invoice_items)
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserService while calculating invoice net value",
                argument={'invoice_items': invoice_items},
                child_error=e,
            )

    @staticmethod
    def _convert_invoice_item_schema_to_invoice_item_model(invoice_item: InvoiceItem) -> InvoiceItemModel:
        try:
            return InvoiceItemModel(
                id=invoice_item.id,
                invoice_id=invoice_item.invoice_id,
                item_description=invoice_item.item_description,
                number_of_items=invoice_item.number_of_items,
                net_value=invoice_item.net_value,
                gross_value=invoice_item.gross_value,
                in_trash=invoice_item.in_trash,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserService while converting invoice item schema to invoice item model",
                argument={'invoice_item': invoice_item},
                child_error=e,
            )

    @staticmethod
    def _convert_invoice_schema_to_invoice_model(invoice: Invoice, user_business_entity: UserBusinessEntityModel, external_business_entity: ExternalBusinessEntityModel, invoice_items: list[InvoiceItemModel] | None, invoice_gross_value: float | None, invoice_net_value: float | None) -> InvoiceModel:
        try:
            return InvoiceModel(
                id=invoice.id,
                user_business_entity=user_business_entity,
                external_business_entity=external_business_entity,
                invoice_pdf=invoice.invoice_pdf,
                invoice_number=invoice.invoice_number,
                issue_date=invoice.issue_date,
                sale_date=invoice.sale_date,
                added_date=invoice.added_date,
                payment_method=invoice.payment_method,
                sum_gross_value=invoice_gross_value,
                sum_net_value=invoice_net_value,
                payment_deadline=invoice.payment_deadline,
                notes=invoice.notes,
                is_settled=invoice.is_settled,
                is_issued=invoice.is_issued,
                in_trash=invoice.in_trash,
                invoice_items=invoice_items,
            )
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in UserService while converting invoice schema to invoice model",
                argument={'invoice': invoice, 'user_business_entity': user_business_entity, 'external_business_entity': external_business_entity ,'invoice_items': invoice_items},
                child_error=e,
            )

    @staticmethod
    def _convert_invoice_removal_bytes_to_dict(invoice_removal: bytes) -> dict[str, uuid.UUID]:
        try:
            invoice_removal: dict[str, str] = ast.literal_eval(invoice_removal.decode('utf-8'))
            invoice_removal_with_uuid: dict[str, uuid.UUID] = {'invoice_id': uuid.UUID(invoice_removal['invoice_id'])}
            return invoice_removal_with_uuid
        except Exception as e:
            raise ServiceError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Unexpected error occurred in InvoiceService while converting invoice removal bytes to dict",
                argument={'invoice_removal': invoice_removal},
                child_error=e,
            )