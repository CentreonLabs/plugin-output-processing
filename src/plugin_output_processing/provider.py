# plugin-output-processing
# Copyright (C) 2024  Centreon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import ollama
import openai
from httpx import ConnectError
from loguru import logger

OLLAMA_NAME = "ollama"
OPENAI_NAME = "openai"


class ProviderError(Exception):
    pass


class Provider:
    name: str
    available: bool = False
    url: str = None
    model: str

    def get_model(
        self,
        list_models: list[str],
        model: str | None = None,
        default_model: str | None = None,
    ) -> str:
        if default_model is None:
            default_model = list_models[0]
        if model is None:
            return default_model
        if model not in list_models:
            logger.warning(f"{model} not found in model list, using default instead.")
            return default_model
        return model


class Ollama(Provider):
    name = OLLAMA_NAME
    url = f"http://{os.environ.get('OLLAMA_HOST', 'localhost')}:11434"

    def __init__(self, model: str = None) -> None:
        self.model = self.fetch_model(model)
        self.available = self.model is not None

    def fetch_model(self, model: str | None = None) -> str | None:
        try:
            models = ollama.list()["models"]
        except ConnectError:
            logger.debug(f"{self.name} is not available.")
            return None
        if len(models) == 0:
            small_model = "qwen2:0.5b"
            logger.warning(
                f"{self.name} can be reached but no models found, downloading {small_model}."
            )
            logger.info("Beware, this will take some time.")
            ollama.pull(small_model)
            return small_model
        list_models = [m["name"] for m in models]
        return self.get_model(list_models, model)


class OpenAI(Provider):
    name = OPENAI_NAME
    model = "gpt-4o"

    def __init__(self, model: str = None) -> None:
        self.available = "OPENAI_API_KEY" in os.environ
        self.model = self.fetch_model(model)

    def fetch_model(self, model: str | None = None) -> str | None:
        if not self.available:
            logger.debug(f"{self.name} is not available.")
            return None

        list_models = [m.id for m in openai.models.list()]
        return self.get_model(list_models, model, self.model)
