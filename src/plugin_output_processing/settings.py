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

from typing import Literal

from loguru import logger
from pydantic import BaseModel, model_validator

from .provider import Ollama, OpenAI


class ProviderError(Exception):
    pass


class Settings(BaseModel):

    provider: Literal["openai", "ollama"] | None = None
    model: str | None = None
    temperature: float = 1
    length: int = 100
    language: Literal["English", "French", "Italian"] = "English"
    role: str = "You are a Centreon professional assistant."
    url: str = None

    @model_validator(mode="after")
    def check_model(self):
        """Make sure all model parameters are set and valid.

        As of today, we support 2 providers, OpenAI and Ollama. If ollama is configured
        and can be called, it will be used as the default provider. If not, OpenAI will
        be used if the API key is set. Otherwise, the service will not start.
        """
        for provider in [Ollama(), OpenAI()]:
            if self.provider and provider.name != self.provider:
                continue
            if provider.available:
                self.provider = provider.name
                self.model = provider.get_model(self.model)
                self.url = provider.url
                logger.debug(
                    f"Provider set to {self.provider} with model {self.model}."
                )
                return self

        raise ProviderError(
            f"No models could be found with configuration: provider={self.provider}, model={self.model}"
        )
