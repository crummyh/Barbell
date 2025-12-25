FROM python:3.12-slim

WORKDIR /code

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY /pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY ./app ./app

COPY ./README.md ./README.md

COPY ./scripts/docker-entrypoint.sh ./scripts/docker-entrypoint.sh
COPY ./scripts/setup.sh ./scripts/setup.sh

RUN chmod +x ./scripts/setup.sh
RUN ./scripts/setup.sh

RUN uv sync --frozen --no-install-project

RUN chmod +x ./scripts/docker-entrypoint.sh
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
