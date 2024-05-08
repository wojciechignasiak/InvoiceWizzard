from abc import ABC, abstractmethod

class KafkaConsumerABC(ABC):
    
    @abstractmethod
    async def run_consumer(self):
        ...
