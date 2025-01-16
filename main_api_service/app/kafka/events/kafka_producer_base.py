# internal modules
from app.kafka.clients.get_kafka_producer_client import get_kafka_producer_client

#3rd party libraries
from fastapi import Depends
from aiokafka import AIOKafkaProducer

class KafkaProducerBase:
    __slots__ = 'kafka_producer'

    def __init__(self, kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer_client)):
        self.kafka_producer: AIOKafkaProducer = kafka_producer