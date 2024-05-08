from abc import ABC, abstractmethod

class KafkaProducerABC(ABC):

    @abstractmethod
    async def start_kafka_producer(self) -> None:
        ...

    @abstractmethod
    async def stop_kafka_producer(self) -> None:
        ...
        
    @abstractmethod
    async def extracted_invoice_data(self, extracted_data):
        ...
        
    @abstractmethod
    async def exception_occured(self, message):
        ...