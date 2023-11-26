from starlette.requests import Request
from aiokafka.errors import KafkaError
import logging

async def get_kafka_producer_client(request: Request):
    try:
        yield request.app.state.kafka_producer
    except KafkaError as e:
        logging.exception(f"get_kafka_producer_client() Error: {e}")
    