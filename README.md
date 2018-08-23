# TRADR: A real-time trading platform! 

### Description

Tradr is a platofrm that facilitates real time trading for retail investors. Tradr caters directly to individuals who would like to implement a trading strategy based on live updates of financial data but do not have the resources of a hedge fund or large bank. With Tradr I decided to implement an investment strategy known as swing trading - if a stock has been doing well recently, we think it will continue to do well in the future so we'd like to buy it. Conversley if a stock is doing poorly, we think it will continue to do poorly in the future so we'd like to sell it. I thought it would be very interesting to explore what kind of infrastructure is needed to process high velocity streams of data and issue buy/sell orders before we miss our chance to make money (or avoid losing money)!

![alt_text](https://github.com/rkhebel/Insight-DE-2018C-Project/blob/master/images/screenshot.png)

### Purpose and Common Use Cases

The purpose of the project is to create a system such that any organization attempting to perform analysis on batch and streaming data with a variety of data types is able to handle a) the amount of data that needs to be stored, b) the throughput of the streaming data, and c) perform any intermediary computations, sorting, or preprocessing before using an algorithm to make investment decisions. 

### Architecture

Data -> Kafka -> Spark streaming -> mySQL -> Flask

![alt text](https://github.com/rkhebel/Insight-DE-2018C-Project/blob/master/images/pipeline.png)

### Dataset

Variety of sources (NYSE, Federal Reserve, Yahoo Finance, Google Finance). To start, I plan on using historical data to simulate a stream which will also allow me to stress test the system 
