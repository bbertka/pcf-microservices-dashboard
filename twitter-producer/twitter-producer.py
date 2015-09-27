#!/usr/bin/python
import json, os
import cfworker
from twython import TwythonStreamer
import pika

amqp_uri = json.loads(os.environ['VCAP_SERVICES'])['p-rabbitmq'][0]['credentials']['uri']
connection = pika.BlockingConnection( pika.URLParameters(amqp_uri) )
channel = connection.channel()
channel.queue_declare(queue=os.getenv('TASK_QUEUE'), durable=True)

class TwitterProducer(TwythonStreamer):

    def on_success(self, data):
	message = data['text'].encode('utf-8')
        channel.basic_publish(exchange='',routing_key=os.getenv('TASK_QUEUE'), body=message, 
		properties=pika.BasicProperties(
			delivery_mode = 2 #make message persist
		))
        print "[twitter-producer] Sent %s" % message

    def on_error(self, status_code, data):
        print status_code


if __name__=='__main__':

	""" Leave this as is if deploying to CF, otherwise choose
	a port for local deployment (e.g. 8080) """

	worker = cfworker.cfworker( port=int(os.getenv('VCAP_APP_PORT')) )
	worker.start()

	""" These variables can be set in your environment (ideal), or
	hardcoded into the function call """
	stream = TwitterProducer(os.getenv('APP_KEY'), os.getenv('APP_SECRET'),
                    os.getenv('OAUTH_TOKEN'), os.getenv('OAUTH_TOKEN_SECRET') )

	""" You can also set an environment variable to choose what to track, or 
	hard code a list here """
	stream.statuses.filter( track=os.getenv('TRACK') )

	""" stops the HTTP server """
	worker.stop()
