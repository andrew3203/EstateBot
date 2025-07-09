FROM python:3.12-slim-bullseye AS python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN apt-get update -qq && \
    apt-get -yqq upgrade && \
    apt-get install --no-install-recommends -yqq \
    build-essential \
    libpq-dev \
    libpq5 \
    libopenblas-dev \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
     uv sync --locked --no-install-project

ADD . /app

ENV PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

RUN addgroup --system fastapi \
    && adduser --system --ingroup fastapi fastapi

RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/*

COPY compose/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
