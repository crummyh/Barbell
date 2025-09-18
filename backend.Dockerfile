FROM python:3.11-slim

WORKDIR /code

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

RUN uv ./scripts/build_docs.py

COPY ./app ./app
COPY setup.sh setup.sh
COPY ./scripts/docker-entrypoint.sh /entrypoint.sh

RUN chmod +x setup.sh
RUN ./setup.sh

COPY ./docs/structure.yaml ./app/web/templates/docs/structure.yaml

RUN uv sync --frozen

ENTRYPOINT ["/entrypoint.sh"]
