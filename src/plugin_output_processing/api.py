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

from fastapi import FastAPI
from uuid import uuid4, UUID

from .processor import PluginProcessor


app = FastAPI()
processor = PluginProcessor()


@app.get("/get", include_in_schema=False)
def get_prompt(
    type: Literal["host", "service"],
    output: str = "n/a",
    name: str = "n/a",
    description: str = "n/a",
):
    """Build a prompt to be send to a LLM.

    This endpoint is useful if the prompt needs to be modified by the end user before
    being sent to the LLM.
    """
    uuid = uuid4()
    prompt = processor.get_prompt(type, output, name, description, uuid)
    return prompt, uuid


@app.get("/send", include_in_schema=False)
def send_prompt(prompt: str, uuid: UUID):
    return processor.send_prompt(prompt, uuid)


@app.get("/explain")
def explain(
    type: Literal["host", "service"],
    output: str = "n/a",
    name: str = "n/a",
    description: str = "n/a",
):
    """Get an explanation for the output.

    This is a combination of the get and send endpoints.
    """
    uuid = uuid4()
    prompt = processor.get_prompt(type, name, output, description, uuid)
    return processor.send_prompt(prompt, uuid)
