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

from loguru import logger
from pydantic import (
    BaseModel,
    field_validator,
    ValidationInfo,
    field_serializer,
)

from pop.providers import Ollama, OpenAI
from pop.globals import Provider, Language

# Disable traceback in case of error, cleaner logs especially for REST API
sys.tracebacklimit = 0


class ProviderError(Exception):
    pass


providers = {Provider.OPENAI: OpenAI(), Provider.OLLAMA: Ollama()}


class Settings(BaseModel):

    provider: Provider | None = None
    model: str | None = None
    temperature: float = 1
    length: int = 100
    language: Language = Language.ENGLISH
    role: str = "You are a Centreon professional assistant."
    url: str | None = None

    @field_serializer("provider", "language")
    def serialize_enum(self, enum: Enum | None) -> str:
        return enum.value if isinstance(enum, Enum) else None

    @field_validator("provider")
    @classmethod
    def check_provider(cls, name: str) -> str:

        while len(providers) > 0:
            provider = providers.pop(name, None)
            provider = provider or providers.popitem()[1]
            provider.fetch()
            if provider.available:
                providers[Provider(value=provider.name)] = provider
                return provider.name

        msg = "None of the providers are available."
        logger.error(msg)
        raise ProviderError(msg)

    @field_validator("model")
    @classmethod
    def check_model(cls, model: str, info: ValidationInfo) -> str:

        provider = providers.get(info.data["provider"])
        if model not in provider.models:
            model = provider.default
        return model

    @field_validator("url")
    @classmethod
    def set_url(cls, url: str, info: ValidationInfo) -> str:

        provider = providers.get(info.data["provider"])
        return provider.url
