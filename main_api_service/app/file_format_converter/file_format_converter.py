#1st party modules
from io import BytesIO
import os
import shutil
from pathlib import Path
import asyncio
from typing import Protocol
from uuid import UUID

class IFileFormatConverter(Protocol):

    async def convert_file_format(self, file_data: bytes | str) -> bytes:
        ...
