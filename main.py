global data
data = [
    {"attack": "Normal", "attack_count_by_type": 0},
    {"attack": "Dos", "attack_count_by_type": 0},
    {"attack": "Probe", "attack_count_by_type": 0},
    {"attack": "Privilege", "attack_count_by_type": 0},
    {"attack": "Access", "attack_count_by_type": 0}
]

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

def main():
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, sum
    # Créer un DataFrame avec les données que vous souhaitez insérer

    # columns = ["attack", "attack_count_by_type"]
    # insert_df = spark.createDataFrame(data, columns)

    # Écrire le DataFrame dans la table PostgreSQL en mode "append"
    # insert_df.write.jdbc(url, "idf_attacks", mode="append", properties=properties)
    data = handle_data_attack("Normal", data)
    print(data)


if __name__ == '__main__':
    main()