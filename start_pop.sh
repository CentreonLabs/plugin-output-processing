#!/bin/bash

set -e
set -x

# Install curl
apt-get update && apt-get install -y curl

# Wait until the ollama service is fully up
until curl -s http://ollama:11434 >/dev/null; do
    echo "Waiting for ollama to be ready..."
    sleep 5
done

# Run the necessary command in the ollama container
curl -X POST http://ollama:11434/api/pull -d '{"name": "qwen2:0.5b"}'

# Start the pop service
exec "$@"
