from modules.initialize_models_utility.initialize_models_abc import InitializeModelsABC
from modules.logging.logging import logger
from httpx import Response, AsyncClient
import os

class InitializeModels(InitializeModelsABC):
    def __init__(self):
        self.__ollama_host: str = os.getenv('OLLAMA_HOST')
        self.__ollama_port: str = os.getenv('OLLAMA_PORT')
        self.__ollama_models: list = ["openchat:latest"]
        self.__async_client = AsyncClient()

    async def initialize_models(self) -> None:
        try:
            print(f"Initializing models: {self.__ollama_models}")
            arledy_existing_models: dict = await self._get_models()
            missing_models: list = await self._extract_missing_models(arledy_existing_models)
            if missing_models:
                print(f"Missing models: {missing_models}")
                print("Downloading missing moddels...")
                await self._pull_models()
                print(f"Models initialized: {self.__ollama_models}!")
            else:
                print(f"All models arleady initialized!")
        except Exception as e:
            logger.error(f"InitializeModels.initialize_models() Error: {e}")
            raise Exception(f"InitializeModels.initialize_models() Error: {e}")

    async def _get_models(self) -> dict:
        try:
            result: Response = await self.__async_client.get(f"http://{self.__ollama_host}:{self.__ollama_port}/api/tags")
            return result.json()
        except Exception as e:
            logger.error(f"InitializeModels._get_models() Error: {e}")
            raise Exception(f"InitializeModels._get_models() Error: {e}")

    async def _extract_missing_models(self, exisiting_models: dict) -> list:
        try:
            exisiting_models_list: list = [model["name"] for model in exisiting_models["models"]]
            missing_models: list = list(set(self.__ollama_models) - set(exisiting_models_list))
            return missing_models
        except Exception as e:
            logger.error(f"InitializeModels._extract_missing_models() Error: {e}")
            raise Exception(f"InitializeModels._extract_missing_models() Error: {e}")

    async def _pull_models(self) -> None:
        try:
            for model in self.__ollama_models:
                body: dict = {}
                body["name"] = model
                await self.__async_client.post(f"http://{self.__ollama_host}:{self.__ollama_port}/api/pull", json=body)
        except Exception as e:
            logger.error(f"InitializeModels._pull_models() Error: {e}")
            raise Exception(f"InitializeModels._pull_models() Error: {e}")