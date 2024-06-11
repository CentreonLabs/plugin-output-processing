import os

import openai
import yaml
from litellm import completion
from loguru import logger
from uuid import UUID

from .settings import Settings


class PluginProcessor:

    def __init__(self):

        self._configure()
        self.prompts = {}

    def send_prompt(self, prompt: str, uuid: UUID) -> str:
        """Send resquest the LLM and handle its response."""

        model = self.settings.model
        provider = self.settings.provider

        alter = prompt != self.prompts[uuid]
        logger.info(
            f"PROMPT: {prompt}, ALTER: {alter}, UUID: {uuid}, PROVIDER: {provider}, MODEL: {model}"
        )

        try:
            response = completion(
                model=f"{provider}/{model}",
                base_url=self.settings.url,
                temperature=self.settings.temperature,
                messages=[
                    {"role": "system", "content": self.settings.role},
                    {"role": "user", "content": self.prompt},
                ],
            )

        except openai.APIError as e:
            content = e.message
            logger.error(
                f"MESSAGE: {e.message}, CODE: {e.status_code}, UUID: {uuid}, PROVIDER: {provider}, MODEL: {model}"
            )

        else:
            content = response.choices[0].message.content

            logger.info(
                f"EXPLANATION: {content}, PROVIDER: {provider}, MODEL: {model}, UUID: {uuid}"
            )

        finally:
            return content

    def get_prompt(
        self, type: str, name: str, output: str, description: str, uuid: UUID
    ):
        """Convert request into a prompt."""

        logger.info(f"TYPE: {type}, NAME: {name}, OUTPUT: {output}, UUID: {uuid}")

        template = """
            Explain the following output coming from a Centreon plugin: {output}. 
            Here are some information about the monitored ressource,
            Type: {type}
            Name: {name}
            Description: {description}
            Describe mains reasons causing this output and suggest the better way to solve it.
            Limit your answer to {length} words and answer in {language}.
            """

        prompt = template.format(
            output=output,
            type=type,
            name=name,
            description=description,
            length=self.settings.length,
            language=self.settings.language,
        )

        self.prompts[uuid] = prompt

        logger.info(f"PROMPT: {prompt}, UUID: {uuid}")

        return prompt

    def _configure(self):
        """Load params from config file and create one if it not exists."""

        # Default path to the root of the project if not provided.
        default_path = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        )
        path = os.environ.get("POP_CONFIG_PATH", default_path)

        try:
            with open(path, "r") as file:
                config = yaml.safe_load(file)
                if not config:
                    raise FileNotFoundError
                self.settings = Settings(**config)
                logger.debug(f"Configuration loaded from: {path}\n")

        except FileNotFoundError:
            with open(path, "w") as file:
                self.settings = Settings()
                yaml.safe_dump(self.settings.model_dump(), file)
                logger.debug(f"Configuration created at: {path}\n")
