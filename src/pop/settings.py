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

from pydantic import BaseModel, Field, ValidationInfo, field_serializer, field_validator

from pop.globals import DEFAULT_ROLE, Language, Provider
from pop.logger import logger
from pop.providers import PROVIDERS

# Disable traceback in case of error, cleaner logs especially for REST API
sys.tracebacklimit = 0


class Settings(BaseModel):

    provider: Provider | None = Field(default=None, validate_default=True)
    model: str | None = Field(default=None, validate_default=True)
    url: str | None = Field(default=None, validate_default=True)
    temperature: float = 1
    length: int = 100
    language: Language = Language.ENGLISH
    role: str = DEFAULT_ROLE

    @field_serializer("provider", "language")
    def serialize_enum(self, enum: Enum | None) -> str:
        """
        This method is needed to write enum fields in the configuration file.
        """
        return enum.value if isinstance(enum, Enum) else None

    @field_validator("provider")
    @classmethod
    def check_provider(cls, name: Provider) -> Provider:
        """
        Use the provider given by the user, if it's not available try a new one.
        """

        providers = [provider for key, provider in PROVIDERS.items() if key != name]
        if name in PROVIDERS:
            providers.insert(0, PROVIDERS.get(name))

        for provider in providers:
            provider.fetch()
            if not provider.available:
                logger.warning(
                    f"{provider.name} is not available. Trying another provider."
                )
                continue
            logger.info(f"Using {provider.name} provider.")
            return provider.name

        raise ValueError("None of the providers are available.")

    @field_validator("model")
    @classmethod
    def check_model(cls, model: str, info: ValidationInfo) -> str:
        """
        Check the model depending of those available for the selected provider.
        If the model is not correct, use the default one.
        """
        provider = PROVIDERS.get(info.data.get("provider"))
        if provider is None:
            raise ValueError("Provider not set")
        if model not in provider.models:
            logger.warning(f"{model} is not available for {provider.name}.")
            model = provider.default
        logger.info(f"Using {model} model.")
        return model

    @field_validator("url")
    @classmethod
    def set_url(cls, url: str, info: ValidationInfo) -> str:
        """
        Set the url.
        """
        provider = PROVIDERS.get(info.data.get("provider"))
        if provider is None:
            raise ValueError("Provider not set")
        return provider.url
