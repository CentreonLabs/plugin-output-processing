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
from httpx import ConnectError

from pop.globals import Provider
from pop.logger import logger
from pop.providers.base import BaseProvider


class Ollama(BaseProvider):

    def __init__(self) -> None:

        host = os.environ.get("OLLAMA_HOST", "localhost")

        super().__init__(name=Provider.OLLAMA, url=f"http://{host}:11434")

    def fetch(self) -> None:
        """
        Get available models for Ollama.
        If Ollama is available but has no models, pull a small one.
        """
        try:
            self.models = [model["name"] for model in ollama.list()["models"]]
        except ConnectError:
            self.models = []
        else:
            if len(self.models) == 0:
                self.pull_default_model()

    def pull_default_model(self) -> None:
        """
        Pull a small model in Ollama;
        """
        small_model = os.environ.get("POP_OLLAMA_DEFAULT_MODEL", "qwen2:0.5b")
        try:
            logger.info(f"No models found, pulling default model {small_model} ...")
            ollama.pull(small_model)
        except ConnectError:
            logger.warning(f"Failed to pull default model {small_model}.")
        else:
            logger.info(f"Model {small_model} pulled.")
            self.models.append(small_model)
