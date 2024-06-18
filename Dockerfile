FROM python:3.10-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the code:
COPY src/plugin_output_processing plugin_output_processing

ENV POP_CONFIG_PATH=config.yaml
ENV LOGURU_LEVEL=INFO

# Copy the log configuration file:
COPY docker_log_conf.yaml log_conf.yaml

# Exposing port:
EXPOSE 8000

# Running command:
CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log_conf.yaml", "plugin_output_processing.api:app" ]
