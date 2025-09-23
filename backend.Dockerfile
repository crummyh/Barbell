FROM python:3.11-slim

WORKDIR /code

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY ./app ./app
COPY ./docs ./docs

COPY ./README.md ./README.md

COPY ./scripts/setup.sh ./scripts/setup.sh
COPY ./scripts/build_docs.py ./scripts/build_docs.py
COPY ./scripts/docker-entrypoint.sh /entrypoint.sh

RUN chmod +x ./scripts/setup.sh
RUN ./scripts/setup.sh

RUN .venv/bin/python ./scripts/build_docs.py
COPY ./docs/structure.yaml ./app/web/templates/docs/structure.yaml

RUN uv sync --frozen --no-install-project

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
