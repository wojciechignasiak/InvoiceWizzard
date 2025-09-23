#internal modules
from main_api_service.app.custom_exceptions.custom_exceptions import StorageError
#3rd party modules
from fastapi import status, Request
#1st party modules
from pathlib import Path
import asyncio
from typing import Protocol
from uuid import UUID
from contextlib import asynccontextmanager

class IIOStorage(Protocol):

    async def remove_invoice_file(self, user_id: UUID, invoice_id: UUID) -> None:
        ...

    async def save_invoice_file(self, user_id: UUID, invoice_id: UUID, invoice_file: bytes) -> None:
        ...

    async def get_invoice_file(self, user_id: UUID, invoice_id: UUID) -> Path | None:
        ...


def get_io_storage(request: Request):
        try:
            return request.app.state.io_storage
        except Exception as e:
            raise StorageError(
                message="Unexpected error while getting IO storage",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                child_error=e
            )

class IOStorage(IIOStorage):

    def __init__(self, base_path: str = "invoices"):
        self.base_path = Path(base_path)
        self._file_locks: dict[str, asyncio.Lock] = {}
        self._locks_lock = asyncio.Lock()


    @asynccontextmanager
    async def file_lock(self, file_path: str):
        try:
            async with self._locks_lock:
                if file_path not in self._file_locks:
                    self._file_locks[file_path] = asyncio.Lock()
                lock = self._file_locks[file_path]

            await lock.acquire()
            try:
                yield
            finally:
                lock.release()
                async with self._locks_lock:
                    if not lock.locked() and not lock._waiters:
                        self._file_locks.pop(file_path, None)
        except Exception as e:
            raise StorageError(
                message="Unexpected error while locking file lock",
                argument={
                    "file_path": file_path,
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                child_error=e
            )

    def _get_invoice_path(self, user_id: UUID, invoice_id: UUID) -> Path:
        return self.base_path / str(user_id) / f"{invoice_id}.pdf"

    @staticmethod
    async def _ensure_directory_exists(directory: Path) -> None:
        try:
            await asyncio.to_thread(lambda: Path(directory).mkdir(exist_ok=True))
        except Exception as e:
            raise StorageError(
                message="Unexpected error while ensuring directory exists",
                argument={
                    "directory": directory,
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                child_error=e
            )

    async def remove_invoice_file(self, user_id: UUID, invoice_id: UUID) -> None:
        try:
            file_path: Path = self._get_invoice_path(user_id, invoice_id)
            async with self.file_lock(str(file_path)):
                await asyncio.to_thread(lambda: Path(file_path).unlink(missing_ok=True))
        except Exception as e:
            raise StorageError(
                message="Unexpected error while trying to remove invoice file",
                argument={
                    "user_id": user_id,
                    "invoice_id": invoice_id,
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                child_error=e
            )

    async def add_invoice_file(self, user_id: UUID, invoice_id: UUID, invoice_file: bytes) -> None:
        try:
            file_path: Path = self._get_invoice_path(user_id, invoice_id)
            async with self.file_lock(str(file_path)):
                await asyncio.to_thread(lambda: Path(file_path).write_bytes(invoice_file))
        except Exception as e:
            raise StorageError(
                message="Unexpected error while trying to add invoice file",
                argument={
                    "user_id": user_id,
                    "invoice_id": invoice_id,
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                child_error=e
            )

    async def get_invoice_file(self, user_id: UUID, invoice_id: UUID) -> Path | None:
        try:
            file_path: Path = self._get_invoice_path(user_id, invoice_id)
            async with self.file_lock(str(file_path)):
                if await asyncio.to_thread(lambda: Path(file_path).exists()):
                    return Path(file_path)
                else:
                    return None
        except Exception as e:
            raise StorageError(
                message="Unexpected error while trying to get invoice file",
                argument={
                    "user_id": user_id,
                    "invoice_id": invoice_id,
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                child_error=e
            )