#!/usr/bin/python
import json, os, random, time
import pika
from routing import worker
import analysis
import requests


amqp_uri = json.loads(os.environ['VCAP_SERVICES'])['p-rabbitmq'][0]['credentials']['uri']
connection = pika.BlockingConnection( pika.URLParameters(amqp_uri) )
channel = connection.channel()
channel.queue_declare(queue=os.getenv('TASK_QUEUE'), durable=True)


def getUserURL(tweet):
        if not tweet:
                return None
        user_url = tweet['user']['url']
        return user_url


def getScreenName(tweet):
        if not tweet:
                return None
        screen_name = tweet['user']['screen_name']
        try:
                unicode(screen_name, "ascii")
        except UnicodeError:
                screen_name = unicode(screen_name, "utf-8")
        finally:
                return screen_name

def process(data=None):
	""" Populate Bubble and Semtiment Charts, then send to profile scraper """
	analysis.populate(data)
	homepage = getUserURL(tweet=data)
	screenname = getScreenName(tweet=data)
	headers = {'Content-Type': 'application/json'}
	if homepage and screenname:
		data = { 'homepage': homepage }
		url = "http://%s/linkedin/scan" % os.getenv('PROFILES_FQDN')
		r = requests.post(url, data = json.dumps(data), headers=headers )
		print r.content
	


def callback(ch, method, properties, data):
	print "[twitter-consumer] Processing: %s" % json.loads(data)['text'].encode('utf-8')
	process(data=json.loads(data))
	ch.basic_ack(delivery_tag = method.delivery_tag)


if __name__=='__main__':
        worker.start()

        print '[twitter-consumer] Waiting for tweets...'

	channel.basic_qos(prefetch_count=1)
	channel.basic_consume(callback, queue=os.getenv('TASK_QUEUE') )
	channel.start_consuming()

	#should never get here
	worker.stop()
