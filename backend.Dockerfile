FROM python:3.11-slim

WORKDIR /code

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY ./app ./app
COPY setup.sh setup.sh
COPY ./scripts/docker-entrypoint.sh /entrypoint.sh

RUN chmod +x setup.sh
RUN ./setup.sh

RUN uv sync --frozen

ENTRYPOINT ["/entrypoint.sh"]
