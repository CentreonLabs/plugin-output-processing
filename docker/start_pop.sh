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

#!/bin/bash

set -e
set -x

# Install curl
apt-get update && apt-get install -y curl jq

# Wait until the ollama service is fully up
until curl -s http://ollama:11434 >/dev/null; do
    echo "Waiting for ollama to be ready..."
    sleep 5
done

# Download a model if no model is present
if [ $(curl http://localhost:11434/api/tags | jq -r '.models | length') -eq 0 ]; then
    curl -X POST http://ollama:11434/api/pull -d '{"name": "qwen2:0.5b"}'
fi

# Start the pop service
exec "$@"
