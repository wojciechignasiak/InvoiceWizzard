#!/bin/sh

echo "Waiting for Redisearch..."

while ! nc -z redisearch 6379; do
  sleep 0.1
done

echo "Redisearch started!"

echo "Waiting for Kafka..."

while ! nc -z kafka 29092; do
  sleep 0.1
done

echo "Kafka started!"

echo "Waiting for Ollama..."

while ! nc -z ollama 11434; do
  sleep 0.1
done

echo "Ollama started!"

exec "$@"