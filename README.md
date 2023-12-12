# idf-real-time-strealing-app

  - ### Git hub
    ```bash
      git clone https://github.com/Abk-coder/idf-real-time-streaming-app.git
    ```
  - ### Docker
    ```bash
      docker compose up  //Lancer docker
    ```
     ```bash
      docker exec -it idf_streaming-spark-1 /opt/bitnami/spark/sbin/start-master.sh    // Lancer spark master
    ```
       ```bash
      docker ps  // Pour récuperer les container ids
    ```
     ```bash
      docker exec -it idf_streaming-spark-1 /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://<CONTAINER-ID de idf_streaming-spark-1>:7077  //Lancer le worker
    ```
    ```bash
      docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER-ID de idf_streaming-kafka-1>  // Pour récuperer l'adresse IP du conteneur idf_streaming-kafka-1
    ```
    ```bash
      python kafka_producer.py  <IP-ADDRESS de idf_streaming-kafka-1>  // Pour lancer le producer kafka
    ```
     ```bash
      python kafka_consumer.py  <IP-ADDRESS de idf_streaming-kafka-1>  // Pour lancer le consumer kafka
    ```
    ``` bash
      docker exec -it idf_streaming-spark-1 spark-submit --master spark://<CONTAINER-ID de idf_streaming-spark-1>:7077 --driver-class-path /opt/bitnami/spark/jars/postgresql-42.7.1.jar --jars        
      /opt/bitnami/spark/jars/postgresql-42.7.1.jar --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0  /opt/bitnami/spark/pysparkprocessing.py  // Lancer l'application
    ```
- ### Postgres
   ```bash
      docker exec -it idf_streaming-postgres-1 bash   // Lancer postgres
    ```
   ```bash
      psql -U postgresuser -h postgres -p 5432 -d testdb   // Lancer la base de données testdb
    ```
   ```bash
      SELECT * FROM idf_attacks;   // Afficher le contenu de la table idf_attacks.
    ```
- ### Grafana
[localhost:3000](http://localhost:3000)   // Ouvre l'interface Grafana

