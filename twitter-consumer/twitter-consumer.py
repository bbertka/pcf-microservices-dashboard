#!/usr/bin/python
import json, os, random, time
import cfworker
import pika

worker = cfworker.cfworker( port=int(os.getenv('VCAP_APP_PORT')) )
worker.start()

amqp_uri = json.loads(os.environ['VCAP_SERVICES'])['p-rabbitmq'][0]['credentials']['uri']
connection = pika.BlockingConnection( pika.URLParameters(amqp_uri) )

channel = connection.channel()

channel.queue_declare(queue=os.getenv('TASK_QUEUE'), durable=True)
print '[twitter-consumer] Waiting for tweets...'

def process():
	""" Processes the tweet, we can anything here """
	time.sleep( random.randint(0, 5) )

def callback(ch, method, properties, body):
	print "[twitter-consumer] Processing: %s" % body
        process()
	ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=os.getenv('TASK_QUEUE') )

channel.start_consuming()

#should never get here
worker.stop()
