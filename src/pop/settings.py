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
from enum import Enum


from pydantic import BaseModel, field_validator, ValidationInfo, field_serializer, Field

from pop.providers import Ollama, OpenAI
from pop.globals import Provider, Language
from pop.logger import logger

# Disable traceback in case of error, cleaner logs especially for REST API
sys.tracebacklimit = 0


providers = {Provider.OPENAI: OpenAI(), Provider.OLLAMA: Ollama()}


class ProviderNotAvailableError(Exception):
    pass


class Settings(BaseModel):

    provider: Provider | None = Field(default=None, validate_default=True)
    model: str | None = Field(default=None, validate_default=True)
    url: str | None = Field(default=None, validate_default=True)
    temperature: float = 1
    length: int = 100
    language: Language = Language.ENGLISH
    role: str = "You are a Centreon professional assistant."

    @field_serializer("provider", "language")
    def serialize_enum(self, enum: Enum | None) -> str:
        return enum.value if isinstance(enum, Enum) else None

    @field_validator("provider")
    @classmethod
    def check_provider(cls, name: Provider) -> Provider:

        while len(providers) > 0:
            provider = providers.pop(name, None)
            provider = provider or providers.popitem()[1]
            provider.fetch()
            if not provider.available:
                logger.warning(
                    f"{provider.name} is not available. Trying another provider."
                )
                continue
            providers[Provider(value=provider.name)] = provider
            logger.info(f"Using {provider.name} provider.")
            return provider.name

        raise ProviderNotAvailableError()

    @field_validator("model")
    @classmethod
    def check_model(cls, model: str, info: ValidationInfo) -> str:

        provider = providers.get(info.data["provider"])
        if model not in provider.models:
            logger.warning(f"{model} is not available for {provider.name}.")
            model = provider.default
        logger.info(f"Using {model} model.")
        return model

    @field_validator("url")
    @classmethod
    def set_url(cls, url: str, info: ValidationInfo) -> str:

        provider = providers.get(info.data["provider"])
        return provider.url
