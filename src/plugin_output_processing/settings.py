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

from .provider import OLLAMA_NAME, OPENAI_NAME, Ollama, OpenAI

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
        # Ollama must be last to be tested first (popitem in the loop)
        providers = {OPENAI_NAME: OpenAI, OLLAMA_NAME: Ollama}
        while [OLLAMA_NAME, OPENAI_NAME]:
            # If a provider is defined in the configuration, we want to test it first
            provider_fun = providers.pop(self.provider, None)
            if provider_fun is None:
                provider_fun = providers.popitem()[1]
            # Only storing the class object allows to test the provider only when needed
            provider = provider_fun(self.model)
            if provider.available:
                logger.info(
                    f"Provider set to {provider.name} with model {provider.model}."
                )
                self.provider = provider.name
                self.model = provider.model
                self.url = provider.url
                return self
            logger.warning(
                f"{provider.name} provider not available, falling back to the next one."
            )
        msg = "None of the providers are available."
        logger.error(msg)
        raise ProviderError(msg)
