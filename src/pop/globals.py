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

from enum import Enum


class Provider(str, Enum):
    """
    Available providers.
    """

    OPENAI = "openai"
    OLLAMA = "ollama"


class Language(str, Enum):
    """
    Available languages for the LLM response.
    """

    FRENCH = "French"
    ENGLISH = "English"
    ITALIAN = "Italian"


DEFAULT_ROLE = """
    You are a Centreon professional assistant.
    """

TEMPLATE_PROMPT = """
    Explain the following output coming from a Centreon plugin: {output}. 
    Here are some information about the monitored ressource,
    Type: {type}
    Name: {name}
    Description: {description}
    Describe mains reasons causing this output and suggest the better way to solve it.
    Ensure your answer is clear, concise, and actionable.
    Limit your answer to {length} words and answer in {language}.
    """
