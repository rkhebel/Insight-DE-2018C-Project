#!/bin/bash

ssh ubuntu@SPARK_IP_ADDRESS '/usr/local/spark/bin/spark-submit --master spark://SPARK_IP_ADDRESS:7077 --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0 --jars /usr/local/spark/jars/postgresql-42.2.4.jar preprocessing.py' &

ssh ubuntu@KAFKA_IP_ADDRESS 'python producer.py'