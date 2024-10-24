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
    Limit your answer to {length} words and answer in {language}.
    """
