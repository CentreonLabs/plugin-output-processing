from typing import Literal

import uvicorn
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
    uuid = uuid4()
    prompt = processor.get_prompt(type, output, name, description, uuid)
    return prompt, uuid


@app.get("/send")
def send_prompt(prompt: str, uuid: UUID):

    response = processor.send_prompt(prompt, uuid)
    return response


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0")
