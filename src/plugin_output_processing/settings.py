import os
from typing import Literal

import ollama
import openai
from pydantic import BaseModel, model_validator
from loguru import logger


class ProviderError(Exception):
    pass


class Settings(BaseModel):

    provider: Literal["openai", "ollama"] | None = None
    model: str | None = None
    url: str | None = None
    temperature: float = 1
    length: int = 100
    language: Literal["English", "French", "Italian"] = "English"
    role: str = "You are a Centreon professional assistant."

    @model_validator(mode="after")
    def check_model(self):
        """Make sure all model parameters are set and valid.

        As of today, we support 2 providers, OpenAI and Ollama. If ollama is configured
        and can be called, it will be used as the default provider. If not, OpenAI will
        be used if the API key is set. Otherwise, the service will not start.
        """
        providers = []
        try:
            ollama_models = [model["name"] for model in ollama.list()["models"]]
            ollama_default = ollama_models[0] if ollama_models else None
            if ollama_default:
                logger.debug(
                    f"Found ollama models: {ollama_models}, default: {ollama_default}"
                )
                providers.append("ollama")
            self.url = f"http://{os.environ.get('OLLAMA_HOST', 'localhost')}:11434"
        except Exception:
            pass

        if os.environ.get("OPENAI_API_KEY"):
            logger.debug("OpenAI API key found.")
            openai_models = [
                model["id"] for model in openai.models.list().model_dump()["data"]
            ]
            providers.append("openai")
            openai_default = "gpt-4o"

        if not providers:
            raise ProviderError("Neither OpenAI nor Ollama can be called.")

        if not self.provider:
            self.provider = providers[0]

        if self.provider == "ollama":
            if not self.model:
                self.model = ollama_default
            if self.model not in ollama_models:
                raise ProviderError(f"Ollama model {self.model} not found.")
        elif self.provider == "openai":
            if not self.model:
                self.model = openai_default
            if self.model not in openai_models:
                raise ProviderError(f"OpenAI model {self.model} not found.")
        logger.debug(f"Using {self.provider} with {self.model}.")

        return self
