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
from uuid import UUID

from fastapi import FastAPI

from pop.processor import PluginProcessor

app = FastAPI()
processor = PluginProcessor()


@app.get("/get", include_in_schema=False)
def get_prompt(
    type: Literal["host", "service"],
    output: str = "n/a",
    name: str = "n/a",
    description: str = "n/a",
):
    """
    Build a prompt to be send to a LLM.

    This endpoint is useful if the prompt needs to be modified by the end user before
    being sent to the LLM.

    Parameters:
    ----------
    type: str
        The type of the prompt. Either "host" or "service".
    output: str
        The output of the plugin.
    name: str, optional
        The name of the host or service.
    description: str, optional
        The description of the host or service.
    """
    return processor.get_prompt(type, name, output, description)


@app.get("/send", include_in_schema=False)
def send_prompt(prompt: str, uuid: UUID):
    """
    Send a prompt to a LLM.

    Parameters:
    ----------
    prompt: str
        The prompt to send to the LLM.
    uuid: UUID
        The UUID of the prompt given by the get endpoint.
    """
    return processor.send_prompt(prompt, uuid)


@app.get("/explain")
def explain(
    type: Literal["host", "service"],
    output: str = "n/a",
    name: str = "n/a",
    description: str = "n/a",
):
    """
    Get an explanation for the output.

    This is a combination of the get and send endpoints.
    """
    prompt, uuid = processor.get_prompt(type, name, output, description)
    return processor.send_prompt(prompt, uuid)
