#!/bin/sh

echo "Running alembic migration..."

docker-compose exec -T main_api_service alembic upgrade head

echo "Alembic migration finished!"