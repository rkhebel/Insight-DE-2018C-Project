############################################################
# Author: Ryan Hebel

# Purpose: To create a Kafka producer
# that reads data from a S3 bucket and sends it to a topic.
############################################################

from kafka import KafkaProducer
import time
import boto3
import botocore
import pandas as pd

def main():

        #create Kafka producer that communicates with master node of ec2 instance running Kafka
        producer = KafkaProducer(bootstrap_servers = 'KAFKA_IP_ADDRESS:9092')

        #creates bucket that points to data
        s3 = boto3.resource('s3', aws_access_key_id = 'AWS_ACCESS_KEY_ID', aws_secret_access_key = 'AWS_SECRET_ACCESS_KEY')
        bucket = s3.Bucket('deutsche-boerse-xetra-pds')

        #the deutsche-boerse-xetra-pds bucket contains a list of csv links that point to data for each hour of trading
        #first, iterate through each object (link to csv) in the bucket
        for object in bucket.objects.all():
                #filter for non-trading hours (empty csv) by size
                if object.size > 136:
                        url = 'https://s3.eu-central-1.amazonaws.com/deutsche-boerse-xetra-pds/' + object.key
                        data = pd.read_csv(url)
                        #read through each line of csv and send the line to the kafka topic
                        for index, row in data.iterrows():
                                output = ''
                                for element in row:
                                        output = output + str(element) + "^"
                                producer.send('rawDBGData', output.encode())
                                producer.flush()

        return

if __name__ == '__main__':
        main()

