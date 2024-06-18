import os

import ollama
import openai
from loguru import logger


class ProviderError(Exception):
    pass


class Provider:

    name: str
    models: list[str] = []
    url: str = None
    available: bool

    def get_model(self, model) -> str:
        if not model:
            logger.warning(f"Model not set for {self.name}. Using default.")
            model = self.default
        if model not in self.models:
            logger.warning(f"Model {model} not found in {self.name} models.")
            model = self.default
        return model


class Ollama(Provider):

    name = "ollama"

    def __init__(self, url: str = None) -> None:
        if not url:
            url = f"http://{os.environ.get('OLLAMA_HOST', 'localhost')}:11434"
        self.url = url
        self.models = self._list_models()
        self.default = self.models[0] if self.models else None
        self.available = self.models != []

    def _list_models(self) -> list[str]:
        try:
            return [model["name"] for model in ollama.list()["models"]]
        except Exception:
            logger.debug(f"Could not list models for {self.name}.")
            return []


class OpenAI(Provider):

    name = "openai"
    default = "gpt-4o"

    def __init__(self) -> None:

        self.available = "OPENAI_API_KEY" in os.environ
        self.models = self._list_models()

    def _list_models(self) -> list[str]:
        if not self.available:
            logger.debug("OpenAI provider not available.")
            return []
        return [model["id"] for model in openai.models.list().model_dump()["data"]]
