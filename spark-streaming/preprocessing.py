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

"""
def sendBuyToSQL(rdd):
        if not rdd.isEmpty():
                df = rdd.take(rdd.count())
                connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
                cursor = connection.cursor()
                for line in df:
                        query = 'INSERT INTO transactions VALUES (%s, %s, %s, %s, %s)'
                        data = (line[0], line[1], line[2], line[3], line[4])
                        cursor.execute(query, data)
                connection.commit()
                connection.close()      
"""

def sendBuyToSQL(rdd):
        connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM portfolio')
        postgres = cursor.fetchall()
        for line in rdd:
                query = 'INSERT INTO transactions VALUES (%s, %s, %s, %s, %s)'
                data = (line[0], line[1], line[2], line[3], line[4])
                cursor.execute(query, data)
                owned = False
                for row in postgres:
                        if line[0] == row[0]:
                                owned = True
                                shares = int(line[4]) + int(row[2])
                                query = 'UPDATE portfolio SET shares = %s WHERE ticker = %s'
                                data = (shares, line[0])
                if not owned:
                        query = 'INSERT INTO portfolio VALUES (%s, %s, %s)'
                        data = (line[0], line[3], line[4])
                cursor.execute(query, data)
        connection.commit()
        connection.close()

def sendSellToSQL(rdd):
        connection = psycopg2.connect(host = 'POSTGRESQL_IP_ADDRESS', database = 'DB_NAME', user = 'DB_USER', password = 'DB_PASSWORD')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM portfolio')
        postgres = cursor.fetchall()
        for line in rdd:
                for row in postgres:
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
        kafkaStream = KafkaUtils.createDirectStream(sparkStreamingContext, ['rawDBGData'], {'metadata.broker.list': 'KAFKA_IP_ADDRESS:9092'})

        filteredStream = kafkaStream.map(lambda line: line[1].split("^"))

        buy = filteredStream.filter(lambda line: (float(line[11]) - float(line[8])) > 0.0).map(lambda line: [line[1], line[6], line[7], line[8], int(1000*(float(line[11]) - float(line[8]))/float(line[8]))]).filter(lambda line: line[4] > 0)

        sell = filteredStream.filter(lambda line: (float(line[11]) - float(line[8])) < 0.0).map(lambda line: [line[1], line[6], line[7], line[8], -1])

        sqlContext = SQLContext(sparkContext)

        buy.foreachRDD(lambda rdd: rdd.foreachPartition(sendBuyToSQL))
        sell.foreachRDD(lambda rdd: rdd.foreachPartition(sendSellToSQL))

        sparkStreamingContext.start()
        sparkStreamingContext.awaitTermination()

        return

if __name__ == '__main__':
        main()
