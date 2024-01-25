from modules.kafka_utilities.kafka_subscriber import KafkaSubscriber


async def main():
    print("AI Service started!")

    kafka_subscriber: KafkaSubscriber = KafkaSubscriber(
        topic="extract_invoice_data"
    )
    await kafka_subscriber.run_consumer()