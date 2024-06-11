from typing import Literal

from fastapi import FastAPI
from uuid import uuid4, UUID

from .processor import PluginProcessor


app = FastAPI()
processor = PluginProcessor()


@app.get("/get")
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


@app.get("/send")
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
    prompt = processor.get_prompt(type, output, name, description, uuid)
    return processor.send_prompt(prompt, uuid)
