from enum import Enum


class Provider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"


class Language(str, Enum):
    """
    Available languages for the LLM response.
    """

    FRENCH = "French"
    ENGLISH = "English"
    ITALIAN = "Italian"
