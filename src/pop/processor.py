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
import sys
from uuid import UUID, uuid4

import yaml
from fastapi import HTTPException, status
from litellm import completion
from pydantic import ValidationError

from pop.globals import TEMPLATE_PROMPT
from pop.logger import logger
from pop.settings import ProviderNotAvailableError, Settings


class PluginProcessor:

    def __init__(self):

        self.configure()
        self.prompts = {}

    def send_prompt(self, prompt: str, uuid: UUID) -> str:
        """Send resquest the LLM and handle its response."""

        model = self.settings.model
        provider = self.settings.provider

        alter = prompt != self.prompts[uuid]

        logger.info(f"Sending prompt with UUID: {uuid} ...")

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
            - temperature: {self.settings.temperature}
            - base_url: {self.settings.url}
            - role: {self.settings.role},
            - prompt: {prompt},
            - error: {e}
            """
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            )

        else:
            logger.info(f"Received response from model {model}.")
            content = response.choices[0].message.content

        return content

    def get_prompt(
        self, type: str, name: str, output: str, description: str
    ) -> tuple[str, UUID]:
        """Convert request into a prompt."""

        uuid = uuid4()

        logger.debug(f"TYPE: {type}, NAME: {name}, OUTPUT: {output}, UUID: {uuid}")

        prompt = TEMPLATE_PROMPT.format(
            output=output,
            type=type,
            name=name,
            description=description,
            length=self.settings.length,
            language=self.settings.language.value,
        )

        self.prompts[uuid] = prompt

        logger.info(f"Prompt created with UUID: {uuid}.")

        return prompt, uuid

    def configure(self):
        """Load params from config file and create one if it doesn't exists."""

        # Default path to the root of the project if not provided.
        default_path = os.path.join(os.getcwd(), "pop.yaml")
        path = os.environ.get("POP_CONFIG_PATH", default_path)

        if not os.path.exists(path):
            with open(path, "w") as f:
                pass

        with open(path, "r") as file:
            config = yaml.safe_load(file)
            config = config if isinstance(config, dict) else {}
            try:
                self.settings = Settings(**config)
            except ValidationError as e:
                logger.error(e)
                sys.exit()
            except ProviderNotAvailableError:
                logger.error("None of the providers are available.")
                sys.exit()

        with open(path, "w") as file:
            yaml.safe_dump(self.settings.model_dump(exclude=["url"]), file)

        logger.info(f"Configuration path: {path}\n")
