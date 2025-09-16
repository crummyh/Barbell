#!/bin/sh
set -e

sleep 1 # Hack to make sure Postgres starts

if [ "$DEBUG" = "true" ]; then
  exec uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
