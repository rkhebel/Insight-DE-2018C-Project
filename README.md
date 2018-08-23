# TRADR: A real-time trading platform! 

### Description

Tradr is a platofrm that facilitates real time trading for retail investors. Tradr caters directly to individuals who would like to implement a trading strategy based on live updates of financial data but do not have the resources of a hedge fund or large bank. 

With Tradr I decided to implement an investment strategy known as swing trading - if a stock has been doing well recently, we think it will continue to do well in the future so we'd like to buy it. Conversley if a stock is doing poorly, we think it will continue to do poorly in the future so we'd like to sell it. 

I thought it would be very interesting to explore what kind of infrastructure is needed to process high velocity streams of data and issue buy/sell orders before we miss our chance to make money (or avoid losing money)!

![alt_text](https://github.com/rkhebel/Insight-DE-2018C-Project/blob/master/images/screenshot.png)

### Architecture

![alt text](https://github.com/rkhebel/Insight-DE-2018C-Project/blob/master/images/pipeline.png)

### Dataset

The dataset that I used to stream data into Tradr is the [Deutsche Börse Public Dataset (PDS)](https://github.com/Deutsche-Boerse/dbg-pds). This data is provided on a minute-by-minute basis and aggregated from the Xetra and Eurex engines, which comprise a variety of equities, funds and derivative securities. The PDS contains details for on a per security level, detailing trading activity by minute including the high, low, first and last prices within the time period. I accessed the data via the S3.

