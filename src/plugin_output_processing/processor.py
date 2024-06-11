import os
import sys

import openai
import yaml
from config_path import ConfigPath
from litellm import completion
from loguru import logger
from uuid import UUID

from .settings import Settings


class PluginProcessor:

    def __init__(self):

        self._configure()
        self._init_logger()
        self.prompts = {}

    def send_prompt(self, prompt: str, uuid: UUID) -> str:
        """Send resquest the LLM and handle its response."""

        self._configure()

        model = self.settings.model
        provider = self.settings.provider

        if not model:
            return "No model provided."

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

        self._configure()

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

        conf_path = ConfigPath("pop", "centreon", ".yaml")
        default_path = conf_path.saveFilePath(mkdir=True)
        path = os.environ.get("POP_CONFIG_PATH", default_path)

        try:
            with open(path, "r") as file:
                config = yaml.safe_load(file)
                self.settings = Settings(**config)
                print(f"Configuration loaded from : {path}\n")

        except FileNotFoundError:
            with open(path, "w") as file:
                self.settings = Settings()
                yaml.safe_dump(self.settings.model_dump(), file)
                print(f"Configuration created at : {path}\n")

    def _init_logger(self):
        """Configure logging to stderr."""

        # remove default configuration
        logger.remove()

        # define our configuration
        logger.add(
            sink=sys.stderr,
            colorize=True,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> {level} <level>{message}</level>",
        )
