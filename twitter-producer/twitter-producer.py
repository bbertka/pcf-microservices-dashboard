#!/usr/bin/python
import json, os, sys, time
import cfworker
from twython import TwythonStreamer
import pika
from flask import Flask

amqp_uri = json.loads(os.environ['VCAP_SERVICES'])['p-rabbitmq'][0]['credentials']['uri']
connection = pika.BlockingConnection( pika.URLParameters(amqp_uri) )
channel = connection.channel()
channel.queue_declare(queue=os.getenv('TASK_QUEUE'), durable=True)

class TwitterProducer(TwythonStreamer):

    def on_success(self, data):
	message = json.dumps(data)
        channel.basic_publish(exchange='',routing_key=os.getenv('TASK_QUEUE'), body=message, 
		properties=pika.BasicProperties(
			delivery_mode = 2 #make message persist
		))
        print "[twitter-producer] Sent: %s" % data['text'].encode('utf-8')

    def on_error(self, status_code, data):
        print "[twitter-producer]: restarting after error: %s" % status_code
	time.sleep(30)
	python = sys.executable
	os.execl(python, python, * sys.argv)


worker = cfworker.cfworker( port=int(os.getenv('PORT')) )
worker.app = Flask(__name__)

@worker.app.route('/topic')
def topic():
	""" Allows other services to query the producer topic """
	return json.dumps({'topic':os.getenv('TOPIC')})

if __name__=='__main__':

	""" Leave this as is if deploying to CF, otherwise choose
	a port for local deployment (e.g. 8080) """

	worker.start()

	""" These variables can be set in your environment (ideal), or
	hardcoded into the function call """
	stream = TwitterProducer(os.getenv('CONSUMER_KEY'), os.getenv('CONSUMER_SECRET'),
                    os.getenv('ACCESS_TOKEN'), os.getenv('ACCESS_TOKEN_SECRET') )

	""" You can also set an environment variable to choose what to track, or 
	hard code a list here """
	stream.statuses.filter( track=os.getenv('TOPIC') )

	""" stops the HTTP server """
	worker.stop()
