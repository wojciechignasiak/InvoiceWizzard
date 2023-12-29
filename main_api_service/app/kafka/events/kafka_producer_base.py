from aiokafka import AIOKafkaProducer

class KafkaProducerBase:
    __slots__ = 'kafka_producer'

    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer: AIOKafkaProducer = kafka_producer