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

import sys
from typing import Literal

from loguru import logger
from pydantic import BaseModel, model_validator

from .provider import OLLAMA_NAME, OPENAI_NAME, Ollama, OpenAI, Provider

# Disable traceback in case of error, cleaner logs especially for REST API
sys.tracebacklimit = 0


class ProviderError(Exception):
    pass


class Settings(BaseModel):

    provider: Literal["openai", "ollama"] | None = None
    model: str | None = None
    temperature: float = 1
    length: int = 100
    language: Literal["English", "French", "Italian"] = "English"
    role: str = "You are a Centreon professional assistant."
    url: str | None = None

    @model_validator(mode="after")
    def check_model(self):
        """Make sure all model parameters are set and valid.

        As of today, we support 2 providers, OpenAI and Ollama. If ollama is configured
        and can be called, it will be used as the default provider. If not, OpenAI will
        be used if the API key is set. Otherwise, the service will not start.
        """
        if self.provider == OLLAMA_NAME or self.provider is None:
            ollama = Ollama(self.model)
            if ollama.available:
                return self.set_provider(ollama)
            if self.provider is not None:
                logger.warning(
                    f"Ollama provider not available, falling back to {OPENAI_NAME}."
                )
                self.provider = None

        if self.provider == OPENAI_NAME or self.provider is None:
            openai = OpenAI(self.model)
            if openai.available:
                return self.set_provider(openai)
            # If OpenAI is set in the configuration but not available, ollama would not
            # have been tried yet. So by recursing, we can try to use ollama as a fallback.
            if self.provider is not None:
                logger.warning(
                    f"OpenAI provider not available, falling back to {OLLAMA_NAME}."
                )
                self.provider = None
                return self.check_model()

        msg = "None of the providers are available."
        logger.error(msg)
        raise ProviderError(msg)

    def set_provider(self, provider: Provider):
        logger.info(f"Provider set to {provider.name} with model {provider.model}.")
        self.provider = provider.name
        self.model = provider.model
        self.url = provider.url
        return self

    def to_dict(self):
        base_dict = {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "length": self.length,
            "language": self.language,
            "role": self.role,
        }
        if self.url is not None:
            base_dict["url"] = self.url
        return base_dict
