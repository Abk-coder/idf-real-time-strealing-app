import random
import time
from datetime import datetime

import pandas
from kafka import KafkaConsumer
from pyspark.sql import SparkSession
import tensorflow as tf
import numpy as np
import pandas as pd
import json
from pyspark.sql.functions import col, count, sum
# Add these lines at the beginning of your pysparkprocessing.py file
import os

from pyspark.sql.types import StructType, StructField, StringType, Row

os.environ['PYSPARK_PYTHON'] = 'python3'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python3'

KAFKA_CONSUMER_GROUP_NAME_CONS = "test-consumer-group"
KAFKA_TOPIC_NAME_CONS = "idftopic"
# PostgreSQL connection parameters
properties = {
    'user': 'postgresuser',
    'password': 'postgrespass',
    "driver": "org.postgresql.Driver"
}
url = "jdbc:postgresql://postgres:5432/testdb"
table_name = "idf_attacks"

attacks = ['Normal', 'Dos', 'Probe', 'Privilege', 'Access']
model = tf.keras.saving.load_model('/opt/bitnami/spark/model')
shared_file_path = '/opt/bitnami/spark/donnees/kakfka_consume_msg.json'


data_attack_list = [
    {"attack": "Normal", "attack_count_by_type": 0},
    {"attack": "Dos", "attack_count_by_type": 0},
    {"attack": "Probe", "attack_count_by_type": 0},
    {"attack": "Privilege", "attack_count_by_type": 0},
    {"attack": "Access", "attack_count_by_type": 0}
]


# predict attack using pretrained model
def predict_attack(data):
    prediction = model.predict(data)
    return attacks[np.argmax(prediction)]

def handle_data_attack(attack, data_attack_list):
    if (attack == 'Normal'):
        data_attack_list[0]["attack_count_by_type"] += 1
    elif (attack == 'Dos'):
        data_attack_list[1]["attack_count_by_type"] += 1
    elif (attack == 'Probe'):
        data_attack_list[2]["attack_count_by_type"] += 1
    elif (attack == 'Privilege'):
        data_attack_list[3]["attack_count_by_type"] += 1
    else:
        data_attack_list[3]["attack_count_by_type"] += 1

    return data_attack_list

def write_to_db(data_df):
    try:
        data_df.write.jdbc(url, table_name, mode="overwrite", properties=properties)
    except Exception as e:
        print(f"Error writing data to PostgreSQL DB: {e}")


# Initialize a Spark session
spark = SparkSession.builder \
    .appName("RealTimeidfDataProcessing") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .getOrCreate()

# Set the log level to show only error messages
spark.sparkContext.setLogLevel("ERROR")


def process_batch(batch_df, epoch_id):
    global idf_message, prediction_data, predicted_attack, idf_df, data_attack_list
    idf_df = pandas.DataFrame()
    csv_file_path = '/opt/bitnami/spark/donnees/x_test.csv'
    print("Kafka Consumer Application Started ... ")
    try:
        # Read the Kafka message from the shared file
        with open(shared_file_path, 'r') as file:
            kafka_message_data = json.load(file)

        idf_message = kafka_message_data['value']
        print("Message received: ", idf_message)

        # Convert the dictionary values to a NumPy array
        print('------- kafka consumer application consumed one record -----------')
        prediction_data = np.array(list(idf_message.values()))
        prediction_data = prediction_data.reshape((1, 17))
        idf_message["timestamp"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        # Convertir le dictionnaire 'idf_message' en DataFrame pandas avec un seul index (index=[0])
        pandas_idf = pd.DataFrame(idf_message, index=[0], columns=list(idf_message).append("timestamp"))
        # Fusionner le DataFrame Spark 'spark_idf' avec le DataFrame Spark 'idf_df'
        idf_df = pd.concat([idf_df, pandas_idf], axis=0, ignore_index=True)

    except Exception as ex:
        print("Failed to read kafka message.")
        print(ex)
    else:
        try:
            print('------- prediction started ------------')
            # Appeler la fonction chargé de faire la prediction et renvoyé l'attaque prédite
            predicted_attack = predict_attack(prediction_data)
            print('predicted attack', predicted_attack)
            print('------- prediction ended ------------')
        except Exception as ex:
            print("prediction failed")
            print(ex)
        else:
            try:
                # creation du dataframe des données à écrire dans la db
                print('----------- writing to db started ------------')
                data_attack_list = handle_data_attack(predicted_attack, data_attack_list)
                # Créer un DataFrame à partir de la liste de dictionnaires
                insert_df = spark.createDataFrame(data_attack_list)
                write_to_db(insert_df)
                print('----------- a writing to db ended ------------')

            except Exception as ex:
                print("Failed to write data to postgresql db")
                print(ex)


if __name__ == "__main__":
    print("L'application a démarré")
    """
    Configurer le flux de sortie en utilisant la méthode 'writeStream'
    Chaque lot de données reçu sera traité en utilisant la fonction 'process_batch'
    La méthode 'foreachBatch' permet d'appliquer une fonction personnalisée à chaque lot de données reçu
    La fonction 'process_batch' doit être définie ailleurs dans le code pour traiter les données du lot
    La méthode 'trigger' spécifie la fréquence à laquelle le traitement des lots de données sera déclenché
    Dans ce cas, le traitement sera déclenché toutes les "15 minutes"
    La méthode 'start' démarre le traitement en streaming
    La méthode 'awaitTermination' bloque le programme en attendant que le flux en streaming se termine
    """
    streaming_df = spark.readStream.format("rate").load()
    query = streaming_df \
        .writeStream \
        .foreachBatch(process_batch) \
        .trigger(processingTime="10 seconds") \
        .start() \
        .awaitTermination()
