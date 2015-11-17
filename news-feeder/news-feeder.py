#!/usr/bin/python
import json, os
from flask import Flask, request, redirect, url_for, send_from_directory, make_response, current_app
from functools import update_wrapper
from datetime import timedelta
import requests

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



app = Flask(__name__,static_url_path='')

@app.route('/')
def keen_chart():
        return app.send_static_file('index.html')

@app.route('/autosearch')
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
