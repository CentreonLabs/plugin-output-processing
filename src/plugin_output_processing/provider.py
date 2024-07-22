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
from typing import List

OLLAMA_NAME = "ollama"
OPENAI_NAME = "openai"


class ProviderError(Exception):
    pass


class Provider:

    def __init__(self):

        self.models = self.list_models()
        if len(self.models) != 0:
            self.available = True
            if not self.default:
                self.default = self.models[0]
        else:
            self.available = False


class OpenAI(Provider):
    name = OPENAI_NAME
    url = None
    default = "gpt-4o"

    def list_models(self) -> List[str]:
        try:
            models = [model.id for model in openai.models.list() if "gpt" in model.id]
        except openai.OpenAIError:
            models = []
        finally:
            return models


class Ollama(Provider):

    name = OLLAMA_NAME
    host = os.environ.get("OLLAMA_HOST", "localhost")
    url = f"http://{host}:11434"
    default = None

    def list_models(self) -> List[str]:
        try:
            models = [model["name"] for model in ollama.list()["models"]]
        except ConnectError:
            logger.error("Could not connect to Ollama server.")
            models = []
        else:
            if len(models) != 0:
                self.pull_default_model(models)
        finally:
            return models

    def pull_default_model(self, models) -> None:
        small_model = os.environ.get("POP_OLLAMA_DEFAULT_MODEL", "qwen2:0.5b")
        try:
            ollama.pull(small_model)
        except ConnectError:
            logger.error(f"{small_model} is not available.")
        else:
            models.append(small_model)


providers = {OPENAI_NAME: OpenAI, OLLAMA_NAME: Ollama}
