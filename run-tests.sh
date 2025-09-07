#!/bin/bash
set -euo pipefail

# Run tests inside Docker

echo "Stopping old test DB (if running)..."
docker compose stop test-db || true
docker-compose down -v

echo "Removing old test DB volume..."
docker compose down -v --remove-orphans test-db || true

echo "Building tests..."
docker compose build test

echo "Starting mail server..."
docker compose up -d mailpit

echo "Starting fresh test DB..."
docker compose up -d test-db

echo "Running tests..."
docker compose run --rm test "$@"

echo "Cleaning up..."
docker compose down -v --remove-orphans test-db
docker compose down -v --remove-orphans mailpit
