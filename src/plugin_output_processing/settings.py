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
from typing import Literal

from .provider import providers

import ollama
import openai
from pydantic import BaseModel, model_validator
from loguru import logger


class ProviderError(Exception):
    pass


class Settings(BaseModel):

    provider: str | None = None
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

        available_providers = {
            key: provider for key, provider in providers.items() if provider.available
        }

        if not available_providers:
            raise ProviderError("Neither OpenAI nor Ollama can be called.")

        if self.provider not in available_providers:

            default_provider = list(available_providers.values())[0]
            self.provider = default_provider.name
            self.model = default_provider.default
            self.url = default_provider.url
            logger.debug(
                f"Provider not found. Switching to {self.model} from {self.provider}."
            )
            return self

        if self.model not in available_providers[self.provider].models:

            self.model = available_providers[self.provider].default
            self.url = available_providers[self.provider].url
            logger.debug(f"Model not found. Switching to {self.model}.")
            return self

        self.url = available_providers[self.provider].url
        logger.debug(f"Using {self.provider} with {self.model}.")
        return self
