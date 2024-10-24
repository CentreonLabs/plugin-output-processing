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

# Set working directory:
WORKDIR /code

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml README.md /code/

# Install dependencies:
 RUN poetry install --no-root --without dev

# Copy the source code:
COPY src/pop pop

# Install project:
RUN poetry install --without dev

# Exposing port:
EXPOSE 8000

# Running command:
CMD ["poetry", "run", "pop"]
#CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log_conf.yaml", "pop.api:app" ]
