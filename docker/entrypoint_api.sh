#!/bin/sh
#
# This file is part of the Centreon Labs plugin-output-processing project.
# (c) Centreon 2024
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# This script is the entrypoint for the API container in the Centreon Labs plugin-output-processing project.

set -e

SECONDS=0
OLLAMA_HOST=${OLLAMA_HOST:-ollama}

# Here we mimic a conditional behavior based on docker compose profile:
#   - Either we want to start the API with ollama model
#   - Or we want to start the API with openai model
# The condition is based on the availability of the ollama service.
echo "Checking ollama availability..."
until curl -s http://${OLLAMA_HOST}:11434/api/tags >/dev/null; do
    if [ $SECONDS -ge 3 ]; then
        break
    fi
    sleep 1
    SECONDS=$((SECONDS + 1))
done

if [ $SECONDS -ge 3 ]; then
    if [ -z "${OPENAI_API_KEY}" ]; then
        echo "Nor ollama or openai model available, exiting..."
        exit 1
    else
        echo "Ollama is not available, using openai model"
    fi
else
    # If a model already exists on ollama, we don't need to pull one and the first one listed will be used
    if [ $(curl http://${OLLAMA_HOST}:11434/api/tags | jq -r '.models | length') -eq 0 ]; then
        # As of mid-2024, qwen2:0.5b is the smallest most performant model available
        curl -s -X POST http://${OLLAMA_HOST}:11434/api/pull -d '{"name":"qwen2:0.5b"}'
    fi
fi

exec "$@"
