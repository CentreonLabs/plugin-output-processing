from enum import Enum


class Provider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
