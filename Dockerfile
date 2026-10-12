# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:0.13.0@sha256:cdc6093146eb3ff6a40107b38f008b789e050e77ad87865e381d9917da55a168 AS uv
FROM python:3.14-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d AS build
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN uv sync --locked --no-dev

FROM python:3.14-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        libssl3t64=3.5.7-1~deb13u2 \
        openssl=3.5.7-1~deb13u2 \
        openssl-provider-legacy=3.5.7-1~deb13u2 \
    && PIP_ROOT_USER_ACTION=ignore python -m pip uninstall --yes pip \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --system --uid 10001 --create-home app
USER 10001
WORKDIR /app
COPY --from=build --chown=10001:10001 /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "portable_agent_calendar.main:app", "--host", "0.0.0.0", "--port", "8080"]
