import os
import requests
from typing import List, Dict



class InitializeModels:
    def __init__(self):
        self.__ollama_host: str = os.getenv('OLLAMA_HOST')
        self.__ollama_port: str = os.getenv('OLLAMA_PORT')
        self.__ollama_models: List = ["openchat:latest", "llava:latest"]

    def initialize_models(self):
        print(f"Initializing models: {self.__ollama_models}")
        arledy_existing_models: Dict = self.__get_models()
        missing_models: List = self.__extract_missing_models(arledy_existing_models)
        if missing_models:
            print(f"Missing models: {missing_models}")
            print("Downloading missing moddels...")
            self.__pull_models()
            print(f"Models initialized: {self.__ollama_models}!")
        else:
            print(f"All models arleady initialized!")

    def __get_models(self):
        result = requests.get(f"http://{self.__ollama_host}:{self.__ollama_port}/api/tags")
        return result.json()

    def __extract_missing_models(self, exisiting_models: Dict) -> List:
        exisiting_models_list: List = [model["name"] for model in exisiting_models["models"]]
        missing_models = list(set(self.__ollama_models) - set(exisiting_models_list))
        return missing_models

    def __pull_models(self):
        for model in self.__ollama_models:
            body: Dict = {}
            body["name"] = model
            requests.post(f"http://{self.__ollama_host}:{self.__ollama_port}/api/pull", json=body)
        