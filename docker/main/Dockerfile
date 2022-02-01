FROM python:3.7.5-slim as base

RUN apt-get update

RUN pip install --upgrade pip==22.0.1

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
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# builder-base
FROM base as builder-base

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # deps for installing poetry
    curl \
    # deps for building python deps
    build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY pyproject.toml poetry.lock ./
COPY sports $PYSETUP_PATH/sports

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev

# Final
FROM base as final

RUN useradd -M -r runner

USER runner

COPY --chown=runner:runner --from=builder-base "$PYSETUP_PATH/sports" "$PYSETUP_PATH/sports"
COPY --chown=runner:runner --from=builder-base "$PYSETUP_PATH/.venv" "$PYSETUP_PATH/.venv"

WORKDIR /sports

LABEL version="0.0.1"

EXPOSE 8587
ENV PS1 "\[\033[32m\]\w\[\033[33m\]\[\033[00m\] $ "
