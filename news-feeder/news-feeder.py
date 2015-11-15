#!/usr/bin/python
import json, os
from flask import Flask, request, redirect, url_for, send_from_directory
import requests

app = Flask(__name__,static_url_path='')

@app.route('/')
def keen_chart():
        return app.send_static_file('index.html')

@app.route('/autosearch')
def news_autosearch():
        print "[news-feeder] checking producer"
	url = "http://%s/topic" % os.getenv('PRODUCER_FQDN')
	r = requests.get(url=url)
	topic = r.json()['topic']
        print "[news-feeder] checking topic: %s " % topic
        r = requests.get(url='http://hn.algolia.com/api/v1/search_by_date?restrictSearchableAttributes=url&query=%s'% topic)
        try:
		#news = {'hits': [r.json()['hits'][0], r.json()['hits'][1], r.json()['hits'][2] ]}
                return json.dumps( r.json()['hits'][0] )
        except:
                return {}
        finally:
                print json.dumps(r.json()['hits'][0])

@app.route('/search/<topic>')
def news_query(topic):
        print "[news-feeder] checking topic: %s " % topic
	r = requests.get(url='http://hn.algolia.com/api/v1/search_by_date?restrictSearchableAttributes=url&query=%s'% topic)
	try:
		return json.dumps(r.json()['hits'][0])
	except:
		return {}
	finally:
		print json.dumps(r.json()['hits'][0])

if __name__ == '__main__':
        print '[news-feeder] Waiting for topics...'
        app.run(host='0.0.0.0', port=int(os.getenv('PORT')) )
	#app.run(host='0.0.0.0', port=8888 )
