#!/bin/sh

echo "Waiting for Postgres..."

while ! nc -z postgresql 5432; do
  sleep 0.1
done

echo "Postgres started!"

echo "Waiting for Redis..."

while ! nc -z redis 6379; do
  sleep 0.1
done

echo "Redis started!"

exec "$@"