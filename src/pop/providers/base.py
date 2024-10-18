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


from abc import ABC, abstractmethod

from pop.globals import Provider


class ProviderError(Exception):
    pass


class BaseProvider(ABC):

    def __init__(
        self, name: Provider, default: str | None = None, url: str | None = None
    ) -> None:
        """
        Parameters
        ----------
        name : ProviderName
            The name of the provider.
        default : str, optional
            The default model to use, by default None.
        """
        self.name = name
        self._default = default
        self.url = url

    @abstractmethod
    def fetch(self) -> None:
        """
        Fetch available models from the provider.
        """
        pass

    @property
    def available(self) -> bool:
        """
        Return True if at least one model is available.
        """
        return len(self.models) > 0

    @property
    def default(self) -> str:
        """
        Return the default model if it is available.
        """
        if self._default in self.models:
            return self._default
        if self.available:
            return self.models[0]
        return None