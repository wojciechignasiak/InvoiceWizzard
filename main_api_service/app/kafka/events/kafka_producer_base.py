from aiokafka import AIOKafkaProducer

class KafkaProducerBase:

    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer: AIOKafkaProducer = kafka_producer