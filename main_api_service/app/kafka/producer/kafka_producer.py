from aiokafka import AIOKafkaProducer
import json
import os

class KafkaProducer:

    def __init__(self):
        self.kafka_host = os.getenv('KAFKA_HOST')
        self.kafka_port = os.getenv('KAFKA_PORT')
        self.kafka_url = f'{self.kafka_host}:{self.kafka_port}'
        self.kafka_producer = AIOKafkaProducer(bootstrap_servers=self.kafka_url)

    async def produce_event(self, topic: str, message: dict):
        try:
            await self.kafka_producer.start()
            await self.kafka_producer.send(topic, json.dumps(message).encode('utf-8'))
        except Exception as e:
            print("KafkaProducer error: ", e)
        finally:
            await self.kafka_producer.stop()
