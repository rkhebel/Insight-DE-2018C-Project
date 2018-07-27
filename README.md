# Insight-DE-2018C-Project

### Project Idea

The goal of this project is to create a pipeline that can ingest batch and streaming data of various types (text, numerical, images, etc.) for use in a financial modeling application. Ideally the application will store batch data, performing compuations or preprocessing as needed for later algorithms, and then combine these results with streaming data to make real time investment decisions. The pipeline will need to be able to handle an arbitrary amount of batch data, stream data with a high throughput, and will need ot ensure low latency so that decisions can be made as quickly as possible when reacting to real time events. 

### Purpose and Common Use Cases

The purpose of the project is to create a system such that any organization attempting to perform analysis on batch and streaming data with a variety of data types is able to handle a) the amount of data that needs to be stored, b) the throughput of the streaming data, and c) perform any intermediary computations, sorting, or preprocessing before using an algorithm to make investment decisions. 

### Relevant Technologies

There are relevant technologies applicable to each stage of the pipeline.

##### Storing batch data

S3

HDFS

##### Reading in streaming data

Amazon Kinesis 

RabbitMQ

##### Computing financial metrics, sorting, filtering

Spark

Flink

Kinesis Streams

Kafka Streams

##### Storing final results

MySQL

Redis

##### Output/dashboarding

Flask

### Proposed Architecture

##### Batch Pipeline

Data -> S3 -> Spark -> mySQL -> Flask

##### Stream Pipeline

Data -> Kafka -> Spark streaming -> mySQL -> Flask

### Data

##### Batch Data

XBRL Financial Statements and Notes Data from the SEC (~20GB), tab-deliminated files containing numeric and textual information

##### Streaming Data

Variety of sources (NYSE, Federal Reserve, Yahoo Finance, Google Finance). To start, I plan on using historical data to simulate a stream which will also allow me to stress test the system 
