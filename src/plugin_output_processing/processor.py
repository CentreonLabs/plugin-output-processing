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

import os

import yaml
from litellm import completion
from loguru import logger
from uuid import UUID
from fastapi import status, HTTPException

from .settings import Settings

TEMPLATE_PROMPT = """
Explain the following output coming from a Centreon plugin: {output}. 
Here are some information about the monitored ressource,
Type: {type}
Name: {name}
Description: {description}
Describe mains reasons causing this output and suggest the better way to solve it.
Limit your answer to {length} words and answer in {language}.
"""


class PluginProcessor:

    def __init__(self):

        self._configure()
        self.prompts = {}

    def send_prompt(self, prompt: str, uuid: UUID) -> str:
        """Send resquest the LLM and handle its response."""

        model = self.settings.model
        provider = self.settings.provider

        alter = prompt != self.prompts[uuid]
        logger.debug(
            f"PROMPT: {prompt}, ALTER: {alter}, UUID: {uuid}, PROVIDER: {provider}, MODEL: {model}"  # noqa E501
        )

        try:
            response = completion(
                model=f"{provider}/{model}",
                base_url=self.settings.url,
                temperature=self.settings.temperature,
                messages=[
                    {"role": "system", "content": self.settings.role},
                    {"role": "user", "content": prompt},
                ],
            )

        except Exception as e:
            msg = f"""Could not provide a completion:
            - model: {provider}/{model}
            - base_url: {self.settings.url}
            - temperature: {self.settings.temperature}
            - role: {self.settings.role},
            - prompt: {prompt},
            - error: {e}
            """

            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

        content = response.choices[0].message.content

        logger.debug(
            f"EXPLANATION: {content}, PROVIDER: {provider}, MODEL: {model}, UUID: {uuid}"  # noqa E501
        )

        return content

    def get_prompt(
        self, type: str, name: str, output: str, description: str, uuid: UUID
    ):
        """Convert request into a prompt."""

        logger.debug(f"TYPE: {type}, NAME: {name}, OUTPUT: {output}, UUID: {uuid}")

        prompt = TEMPLATE_PROMPT.format(
            output=output,
            type=type,
            name=name,
            description=description,
            length=self.settings.length,
            language=self.settings.language,
        )

        self.prompts[uuid] = prompt

        return prompt

    def _configure(self):
        """Load params from config file and create one if it doesn't exists."""

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
