#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z postgresql 5432; do
  sleep 0.1
done

echo "PostgreSQL started!"

echo "Waiting for Kafka..."

while ! nc -z kafka 29092; do
  sleep 0.1
done

echo "Kafka started!"

exec "$@"