import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from redis.asyncio import Redis, BlockingConnectionPool
from aiokafka.errors import KafkaTimeoutError, KafkaError
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from main_api_service.app.models.kafka_topics_enum import KafkaTopicsEnum
from main_api_service.app.kafka.initialize_topics.startup_topics import startup_topics

class ApplicationStartupProcesses:

    def __init__(self) -> None:
        
        self.postgres_username = os.environ.get("POSTGRES_USERNAME")
        self.postgres_password = os.environ.get("POSTGRES_PASSWORD")
        self.postgres_host = os.environ.get("POSTGRES_HOST")
        self.postgres_port = os.environ.get("POSTGRES_PORT")
        self.postgres_db = os.environ.get("POSTGRES_DB")
        self.postgres_url = f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

        self.redis_password = os.environ.get("REDIS_PASSWORD")
        self.redis_host = os.environ.get("REDIS_HOST")
        self.redis_port = os.environ.get("REDIS_PORT")

        self.kafka_host = os.environ.get("KAFKA_HOST")
        self.kafka_port = os.environ.get("KAFKA_PORT")
        self.kafka_url = f"{self.kafka_host}:{self.kafka_port}"



    async def redis_pool(self) -> BlockingConnectionPool:
        while True:
            try:
                print("Creating Redis connection pool...")
                redis_pool = BlockingConnectionPool(max_connections=3000, host=self.redis_host, port=self.redis_port, password=self.redis_password)
                redis_client: Redis = await Redis(connection_pool=redis_pool)
                print("Testing connection to Redis...")
                redis_info = await redis_client.ping()
                if redis_info:
                    print('Connection to Redis status: Connected')
                    
                else:
                    print('Connection to Redis status: Failed. Retrying...')
                    raise ConnectionError
                return redis_pool
            except ConnectionError:
                await redis_client.close()
                await asyncio.sleep(3)

    async def kafka_topics_initialization(self):
        while True:
            try:
                print("Initializing Kafka topics...")
                await startup_topics(self.kafka_url)
                print("Kafka topics initialized!")
                break
            except KafkaTimeoutError as e:
                print(f'Kafka Timeout error durning topic initialization: {e}')
            except KafkaError as e:
                print(f'Kafka error durning topic initalization: {e}')

    async def kafka_producer(self) -> AIOKafkaProducer:
        while True:
            try:
                print("Running Kafka Producer on separate event loop...")
                loop = asyncio.get_event_loop()
                kafka_producer: AIOKafkaProducer = AIOKafkaProducer(
                    loop=loop, 
                    bootstrap_servers=self.kafka_url)
                return kafka_producer
            except (KafkaError, KafkaTimeoutError) as e:
                print(f'Error occured durning running Kafka Producer: {e}')

    async def kafka_consumer(self) -> AIOKafkaConsumer:
        while True:
            try:
                print("Running Kafka Consumer on separate event loop...")
                loop = asyncio.get_event_loop()
                kafka_consumer: AIOKafkaConsumer = AIOKafkaConsumer(
                    KafkaTopicsEnum.unable_to_extract_invoice_data.value, 
                    KafkaTopicsEnum.extracted_invoice_data.value,
                    loop=loop, 
                    bootstrap_servers=self.kafka_url)
                return kafka_consumer
            except (KafkaError, KafkaTimeoutError) as e:
                print(f'Error occured durning running Kafka Consumer: {e}')