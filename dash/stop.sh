#!/bin/bash

ssh ubuntu@SPARK_IP_ADDRESS 'pkill -f preprocessing.py' &

ssh ubuntu@KAFKA_IP_ADDRESS 'pkill -f producer.py'