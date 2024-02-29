from aiokafka import AIOKafkaConsumer
from asyncio import AbstractEventLoop
from modules.kafka_utilities.kafka_consumer_abc import KafkaConsumerABC
from modules.models.kafka_topics_enum import KafkaTopicsEnum
import os


class KafkaConsumer(KafkaConsumerABC):
    def __init__(self, loop: AbstractEventLoop):
        self.host = os.getenv("KAFKA_HOST")
        self.port = os.getenv("KAFKA_PORT")
        self.consumer = AIOKafkaConsumer(
            KafkaTopicsEnum.account_registered.value,
            KafkaTopicsEnum.account_confirmed.value,
            KafkaTopicsEnum.change_email.value,
            KafkaTopicsEnum.email_changed.value,
            KafkaTopicsEnum.change_password.value,
            KafkaTopicsEnum.password_changed.value,
            KafkaTopicsEnum.remove_invoice.value,
            KafkaTopicsEnum.invoice_removed.value,
            KafkaTopicsEnum.remove_user_business_entity.value,
            KafkaTopicsEnum.user_business_entity_removed.value,
            KafkaTopicsEnum.remove_external_business_entity.value,
            KafkaTopicsEnum.external_business_entity_removed.value,
            KafkaTopicsEnum.reset_password.value, 
            loop=loop, 
            bootstrap_servers=f'{self.host}:{self.port}')

    async def run_consumer(self):
        try:
            print("Notification service started!")
            print("Awaiting for events...")
            await self.consumer.start()
            async for message in self.consumer:
                print("Message recived!")
                match message.topic:
                    case KafkaTopicsEnum.account_registered.value:
                        print(f"{KafkaTopicsEnum.account_registered.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.account_confirmed.value:
                        print(f"{KafkaTopicsEnum.account_confirmed.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.change_email.value:
                        print(f"{KafkaTopicsEnum.change_email.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.email_changed.value:
                        print(f"{KafkaTopicsEnum.email_changed.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.change_password.value:
                        print(f"{KafkaTopicsEnum.change_password.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.password_changed.value:
                        print(f"{KafkaTopicsEnum.password_changed.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.remove_invoice.value:
                        print(f"{KafkaTopicsEnum.remove_invoice.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.invoice_removed.value:
                        print(f"{KafkaTopicsEnum.invoice_removed.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.remove_user_business_entity.value:
                        print(f"{KafkaTopicsEnum.remove_user_business_entity.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.user_business_entity_removed.value:
                        print(f"{KafkaTopicsEnum.user_business_entity_removed.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.remove_external_business_entity.value:
                        print(f"{KafkaTopicsEnum.remove_external_business_entity.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case KafkaTopicsEnum.reset_password.value:
                        print(f"{KafkaTopicsEnum.reset_password.value}:")
                        message = message.value.decode("utf-8")
                        print(message)
                    case _:
                        print("Unknown message recived!")
                        print(message.value)
        except Exception as e:
            print(e)
        finally:
            await self.consumer.stop()
