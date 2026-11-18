# Crypto Data Acquisition and Analytics Pipeline

This project combines live Binance trade ingestion, Kafka, Spark Structured Streaming, HDFS, and Hadoop MapReduce.

## Services

- Kafka KRaft broker: `localhost:9092`
- HDFS NameNode: `http://localhost:9870`
- Hadoop RPC: `localhost:9000`
- Spark Master UI: `http://localhost:8080`
- Jupyter Lab: `http://localhost:8888`
- Spark application UI: `http://localhost:4040`

## Run the Complete Pipeline

1. Build the custom NameNode image and start the stack:

   ```bash
   docker compose up -d --build
   ```

2. Open Jupyter at `http://localhost:8888`.

3. Open a terminal and start the live Binance producer:

   ```bash
   python3 /workspace/binance_producer.py
   ```

   Keep this process running while the streaming pipeline is active.

4. Execute the notebook cells in `crypto_pipeline.ipynb` in order. The notebook:
   - creates the Spark session on `crypto-spark-master:7077`
   - reads live records from the `crypto-trades` Kafka topic
   - calculates one-minute VWAP and trade volume windows
   - stores raw Parquet trades in HDFS
   - creates an HDFS CSV snapshot for MapReduce

5. Run the Hadoop Streaming batch benchmark from inside the NameNode:

   ```bash
   docker exec -it crypto-namenode bash
   time hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
     -files /workspace/mapper.py,/workspace/reducer.py \
     -mapper 'python3 /workspace/mapper.py' \
     -reducer 'python3 /workspace/reducer.py' \
     -input /data/raw/crypto-trades-csv \
     -output /data/output/mr-benchmark-$(date +%s)
   ```

   Use a new output path for every run.

## Useful Checks

```bash
# List containers
docker compose ps

# List Kafka topics
docker exec crypto-kafka sh -lc '/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list'

# Inspect HDFS data
docker exec crypto-namenode sh -lc '/opt/hadoop-3.2.1/bin/hdfs dfs -ls -R /data'

# Inspect the latest MapReduce output
docker exec crypto-namenode sh -lc '/opt/hadoop-3.2.1/bin/hdfs dfs -cat /data/output/mr-benchmark-*/part-*'
```

## Persistence and Reset

The NameNode metadata, DataNode blocks, and Kafka data are stored in Docker named volumes:

- `namenode_data`
- `datanode_data`
- `kafka_data`

Stop the stack without deleting data:

```bash
docker compose down
```

Reset all project data:

```bash
docker compose down -v
```

`-v` deletes the HDFS and Kafka data volumes permanently.
