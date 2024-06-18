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
from loguru import logger


class ProviderError(Exception):
    pass


class Provider:

    name: str
    models: list[str] = []
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

    def __init__(self) -> None:
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
