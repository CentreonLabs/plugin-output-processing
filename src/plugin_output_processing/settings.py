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
from pydantic import BaseModel, field_validator, ValidationInfo, Field

from .provider import providers

# Disable traceback in case of error, cleaner logs especially for REST API
sys.tracebacklimit = 0


class ProviderError(Exception):
    pass


class Settings(BaseModel):

    provider: str | None = Field(default=None, validate_default=True)
    model: str | None = Field(default=None, validate_default=True)
    url: str | None = Field(default=None, validate_default=True)
    temperature: float = 1
    length: int = 100
    language: Literal["English", "French", "Italian"] = "English"
    role: str = "You are a Centreon professional assistant."

    @field_validator("provider")
    @classmethod
    def check_provider(cls, name: str) -> str:

        while providers:
            provider_cls = providers.pop(name, None)
            if provider_cls is None:
                provider_cls = providers.popitem()[1]
            provider = provider_cls()
            if provider.available:
                providers[provider.name] = provider
                return provider.name

        msg = "None of the providers are available."
        logger.error(msg)
        raise ProviderError(msg)

    @field_validator("model")
    @classmethod
    def check_model(cls, model: str, info: ValidationInfo) -> str:

        provider = providers.get(info.data["provider"])
        if model in provider.models:
            return model
        else:
            return provider.default

    @field_validator("url")
    @classmethod
    def set_url(cls, url: str, info: ValidationInfo) -> str:

        provider = providers.get(info.data["provider"])
        return provider.url
