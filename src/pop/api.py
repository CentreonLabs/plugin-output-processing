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

import uvicorn
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI

from pop.processor import PluginProcessor

app = FastAPI()
processor = PluginProcessor()


@app.get("/get", include_in_schema=True)
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
    prompt = processor.get_prompt(
        type=type, name=name, output=output, description=description, uuid=uuid
    )
    return prompt, uuid


@app.get("/send", include_in_schema=True)
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


def main():

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s | %(levelprefix)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": "%(asctime)s | %(levelprefix)s %(message)s",  # noqa: E501
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    uvicorn.run(app, log_config=log_config)
