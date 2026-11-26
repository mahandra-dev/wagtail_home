# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

# uv binary from the official image (pinned minor version).
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    # Keep the venv outside /app so a bind-mounted source tree doesn't hide it.
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g libwebp7 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 app
WORKDIR /app

# Install dependencies first (cached layer), then the project source.
# Dev group included so `make dc-test` works inside the container.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=.python-version,target=.python-version \
    uv sync --frozen --no-install-project

COPY --chown=app:app . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen \
    && mkdir -p /app/media /app/staticfiles && chown -R app:app /app/media /app/staticfiles

USER app
EXPOSE 8000

# Production default: gunicorn with prod settings. docker-compose.yml overrides this for dev.
ENV DJANGO_SETTINGS_MODULE=config.settings.prod
CMD ["uv", "run", "--frozen", "--no-sync", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
