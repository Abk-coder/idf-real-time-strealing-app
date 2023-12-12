import time
import logging
import pandas as pd
import json
from kafka import KafkaProducer

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('kafka-producer')


# Function to generate random weather data for a given city
def read_csv_data(path):
    return pd.read_csv(path)


# Callback for successful message send
def on_send_success(record_metadata):
    log.info(
        f"Message sent to {record_metadata.topic} on partition {record_metadata.partition} with offset {record_metadata.offset}")


# Callback for message send failure (e.g., KafkaError)
def on_send_error(excp):
    log.error('Error sending message', exc_info=excp)


# Serializer to convert to bytes for transmission
def json_serializer(data):
    return json.dumps(data).encode('utf-8')


# Connect to the Kafka server within the Docker network
producer = KafkaProducer(bootstrap_servers=['localhost:29092'], value_serializer=json_serializer)

if __name__ == "__main__":
    df = read_csv_data(r"C:\DIC2\Projets\deepLearning\idf_streaming\donnees\x_test.csv")
    print(df.head(1))
    idf_list = df.to_dict(orient="records")

    for idf_line in idf_list:
        print("Data to be sent: ", idf_line)
        # Asynchronously send the data and add callbacks
        future = producer.send('idftopic', idf_line)
        future.add_callback(on_send_success).add_errback(on_send_error)
        time.sleep(15)

