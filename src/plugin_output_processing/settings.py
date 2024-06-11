import os
from typing import Literal

import ollama
from pydantic import BaseModel, model_validator


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

        opeanai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
        openai_default = "gpt-4o"

        ollama_models = [model["name"] for model in ollama.list()["models"]]
        ollama_default = ollama_models[0] if ollama_models else None
        ollama_host = os.environ.get("OLLAMA_HOST", "localhost")

        providers = {
            "openai": {
                "models": opeanai_models,
                "default": openai_default,
                "url": None,
            },
            "ollama": {
                "models": ollama_models,
                "default": ollama_default,
                "url": f"http://{ollama_host}:11434",
            },
        }

        if self.provider:

            available_models = providers[self.provider]["models"]

            if self.model not in available_models:
                self.model = providers[self.provider]["default"]

            self.url = providers[self.provider]["url"]

        else:
            self.model = None

        return self
