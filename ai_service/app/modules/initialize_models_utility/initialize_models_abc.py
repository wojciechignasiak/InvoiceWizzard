from abc import ABC, abstractmethod


class InitializeModelsABC(ABC):
    
    @abstractmethod
    async def initialize_models(self) -> None:
        ...

    @abstractmethod
    async def _get_models(self) -> dict:
        ...

    @abstractmethod
    async def _extract_missing_models(self, exisiting_models: dict) -> list:
        ...

    @abstractmethod
    async def _pull_models(self) -> None:
        ...
