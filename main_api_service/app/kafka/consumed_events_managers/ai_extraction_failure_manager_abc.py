from typing import (
    Dict
)
from abc import ABC, abstractmethod

class AIExtractionFailureManagerABC(ABC):

    @abstractmethod
    async def create_ai_extraction_failure(self, message: Dict):
        ...


