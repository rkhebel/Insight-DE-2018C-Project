############################################################
# Author: Ryan Hebel

# Purpose: To consume data from Kafka topic
# and perform computations for trading algorithm.
# 	- identify stocks to buy, stocks to sell, and
#	send these to the database
############################################################

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SQLContext
import psycopg2

#function to send a buy order to postgres
def sendBuyToSQL(rdd):
        #connect to db and fetch all records in portfolio
        connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM portfolio')
        postgres = cursor.fetchall()
        
        #for every buy order in the current rdd
        for line in rdd:
                #insert the buy order into the transactions table
                query = 'INSERT INTO transactions VALUES (%s, %s, %s, %s, %s)'
                data = (line[0], line[1], line[2], line[3], line[4])
                cursor.execute(query, data)
                
                #check to see if the stock is already owned
                # if yes - find the entry in your portfolio and update the number of shares you own (as well as price)
                owned = False
                for row in postgres:
                        if line[0] == row[0]:
                                owned = True
                                shares = int(line[4]) + int(row[2])
                                query = 'UPDATE portfolio SET shares = %s WHERE ticker = %s'
                                data = (shares, line[0])
                                
                # if the stock isn't already owned, add entry into portofolio
                if not owned:
                        query = 'INSERT INTO portfolio VALUES (%s, %s, %s)'
                        data = (line[0], line[3], line[4])
                        
                cursor.execute(query, data)
                
        #close db connection
        connection.commit()
        connection.close()

#function to send sell orders to sql - need to check if stock is owned in order to sell!
def sendSellToSQL(rdd):
        #connect to db and fetch all records in portfolio
        connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM portfolio')
        postgres = cursor.fetchall()
        
        #for each sell order in current rdd
        for line in rdd:
                for row in postgres:
                        #if the stock is owned, record the transaction and remove the stock from your portfolio
                        if line[0] == row[0]:
                                query = 'INSERT INTO transactions VALUES (%s, %s, %s, %s, %s)'
                                data = (line[0], line[1], line[2], line[3], -1*int(row[2]))
                                cursor.execute(query, data)
                                query = 'DELETE FROM portfolio WHERE ticker = %s'
                                data = (line[0],)
                                cursor.execute(query, data)
                                break;
        connection.commit()
        connection.close()

def main():
        sparkContext = SparkContext(appName = 'testJob')
        sparkContext.setLogLevel('ERROR')
        sparkStreamingContext = StreamingContext(sparkContext, 1)
        
        #create DStream that reads from kafka topic 
        kafkaStream = KafkaUtils.createDirectStream(sparkStreamingContext, ['rawDBGData'], {'metadata.broker.list': 'KAFKA_IP_ADDRESS:9092'})
        
        #parse the row into separate components
        filteredStream = kafkaStream.map(lambda line: line[1].split("^"))
        
        #identify the stocks that we would like to buy (those with increasing price) and calculate number of shares to purchase
        buy = filteredStream.filter(lambda line: (float(line[11]) - float(line[8])) > 0.0).map(lambda line: [line[1], line[6], line[7], line[8], int(1000*(float(line[11]) - float(line[8]))/float(line[8]))]).filter(lambda line: line[4] > 0)

        #identify the stocks that we would like to sell (those with decreasing price)
        sell = filteredStream.filter(lambda line: (float(line[11]) - float(line[8])) < 0.0).map(lambda line: [line[1], line[6], line[7], line[8], -1])

        sqlContext = SQLContext(sparkContext)

        #use foreachPartition to reduce the number of database connections that are opened/closed
        buy.foreachRDD(lambda rdd: rdd.foreachPartition(sendBuyToSQL))
        sell.foreachRDD(lambda rdd: rdd.foreachPartition(sendSellToSQL))

        sparkStreamingContext.start()
        sparkStreamingContext.awaitTermination()

        return

if __name__ == '__main__':
        main()
