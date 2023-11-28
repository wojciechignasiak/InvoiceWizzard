from kafka.admin import KafkaAdminClient, NewTopic
from app.models.kafka_topics_enum import KafkaTopicsEnum
import logging

async def startup_topics(kafka_url: str):
    admin_client = KafkaAdminClient(
            bootstrap_servers=f'{kafka_url}',
            security_protocol="PLAINTEXT"
        )
    try:
        topics = admin_client.list_topics()
        existing_topics = topics
        topic_name_list = [
            KafkaTopicsEnum.account_registered.value,
            KafkaTopicsEnum.account_confirmed.value,
            KafkaTopicsEnum.change_email.value,
            KafkaTopicsEnum.email_changed.value,
            KafkaTopicsEnum.change_password.value,
            KafkaTopicsEnum.password_changed.value,
            KafkaTopicsEnum.reset_password.value,
            KafkaTopicsEnum.remove_user_business_entity.value,
            KafkaTopicsEnum.user_business_entity_removed.value
        ]
        topic_list = []
        for topic_name in topic_name_list:
            if topic_name not in existing_topics:
                new_topic: NewTopic = NewTopic(name=topic_name, num_partitions=3, replication_factor=1)
                topic_list.append(new_topic)

        admin_client.create_topics(new_topics=topic_list, validate_only=False)
    except Exception as e:
        logging.exception(f"startup_topics(): {e}")
    finally:
        admin_client.close()