from typing import List

import os
import ollama
import openai

from loguru import logger

OLLAMA = "ollama"
OPENAI = "openai"


class Provider:

    def __init__(
        self,
        name: str,
        models: List[str],
        default: str | None,
        url: str,
        available: bool,
    ) -> None:

        self.name = name
        self.models = models
        self.default = default
        self.url = url
        self.available = available


class Ollama(Provider):

    def __init__(self) -> None:

        models = [model["name"] for model in ollama.list()["models"]]
        default = models[0] if models else None
        hostname = os.environ.get("OLLAMA_HOST", "localhost")
        url = f"http://{hostname}:11434"
        available = models != []

        if available:
            logger.debug(f"Found ollama models: {models}, default: {default}")

        super().__init__(OLLAMA, models, default, url, available)


class OpenAI(Provider):

    def __init__(self) -> None:

        available = "OPENAI_API_KEY" in os.environ
        models = [model.id for model in openai.models.list()] if available else []
        default = "gpt-4o" if available else None
        url = None

        if available:
            logger.debug("OpenAI API key found.")

        super().__init__(OPENAI, models, default, url, available)


providers = {OLLAMA: Ollama(), OPENAI: OpenAI()}
