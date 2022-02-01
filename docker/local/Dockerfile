FROM python:3.7.5-slim as base

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y make openssh-client vim

# python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.1.12 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # poetry to not create the virtual environment
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # path
    # virtual environment will live
    VIRTUAL_ENV="/opt/pysetup/venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m venv $VIRTUAL_ENV

# builder-base
FROM base as builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # deps for installing poetry
    curl unzip \
    # deps for building python deps
    build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python -

# Download Docker Engine CLI - Community Edition
RUN mkdir /docker-ce \
    && cd /docker-ce \
    && curl -O https://download.docker.com/linux/debian/dists/buster/pool/stable/amd64/docker-ce-cli_20.10.8~3-0~debian-buster_amd64.deb

# Download docker-compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Final
FROM base as final

# copy in our built poetry
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
# copy Docker Engine CLI - Community Edition installation file
COPY --from=builder-base /docker-ce/docker-ce-cli_20.10.8~3-0~debian-buster_amd64.deb /docker-ce/docker-ce-cli_20.10.8~3-0~debian-buster_amd64.deb
# copy docker-compose
COPY --from=builder-base /usr/local/bin/docker-compose /usr/local/bin/docker-compose

# Docker & docker-compose
RUN dpkg -i /docker-ce/docker-ce-cli_20.10.8~3-0~debian-buster_amd64.deb
RUN chmod +x /usr/local/bin/docker-compose

WORKDIR /sports

COPY pyproject.toml poetry.lock .sports-completion.sh ./
COPY sports ./sports

RUN poetry run pip install --upgrade pip==22.0.1
RUN poetry install

RUN rm -rf /sports/*

LABEL version="0.0.1"

EXPOSE 8088
