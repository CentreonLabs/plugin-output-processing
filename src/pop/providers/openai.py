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


import openai


from pop.globals import Provider
from pop.providers.base import BaseProvider


class OpenAI(BaseProvider):

    def __init__(self):
        super().__init__(Provider.OPENAI, "gpt-4o")

    def fetch(self):
        try:
            self.models = [
                model.id for model in openai.models.list() if "gpt" in model.id
            ]
        except openai.OpenAIError:
            self.models = []
