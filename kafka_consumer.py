from kafka import KafkaConsumer
from json import loads
import json


class KafkaMessage:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class KafkaConsumerWrapper:
    def __init__(self, group_name, topic_name, bootstrap_servers, output_file):
        self.group_name = group_name
        self.topic_name = topic_name
        self.bootstrap_servers = bootstrap_servers
        self.output_file = output_file
        self.consumer = KafkaConsumer(
            self.topic_name,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=self.group_name,
            value_deserializer=lambda x: loads(x.decode('utf-8'))
        )

    def consume_messages(self):
        for message in self.consumer:
            kafka_message = KafkaMessage(message.key, message.value)
            self.write_to_file(kafka_message)
            yield kafka_message  # Use yield to return messages continuously

    def write_to_file(self, kafka_message):
        with open(self.output_file, 'w') as file:
            json.dump({'key': kafka_message.key, 'value': kafka_message.value}, file)


if __name__ == "__main__":
    KAFKA_CONSUMER_GROUP_NAME_CONS = "test-consumer-group"
    KAFKA_TOPIC_NAME_CONS = "idftopic"
    KAFKA_BOOTSTRAP_SERVERS = 'localhost:29092'

    kafka_consumer = KafkaConsumerWrapper(
        group_name=KAFKA_CONSUMER_GROUP_NAME_CONS,
        topic_name=KAFKA_TOPIC_NAME_CONS,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        output_file=r"C:\DIC2\Projets\deepLearning\idf_streaming\donnees\kakfka_consume_msg.json"
    )

    print("Kafka Consumer Application Started ... ")

    try:
        for kafka_message in kafka_consumer.consume_messages():
            print("Key: ", kafka_message.key)
            print("Message received: ", kafka_message.value)
    except Exception as ex:
        print("Failed to read kafka message.")
        print(ex)
