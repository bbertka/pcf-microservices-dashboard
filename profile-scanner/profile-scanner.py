#!/usr/bin/python
import json, os, random, time
from flask import Flask, request, redirect, url_for, send_from_directory, make_response, current_app
from functools import update_wrapper
from datetime import timedelta
import vscrape as linkedin
import redis
from redis_collections import List


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

def saveProfile(profile=None):
	try:
		print "[profile-scanner] saving profile %s" % profile['url']
		creds = json.loads(os.environ['VCAP_SERVICES'])['p-redis'][0]['credentials']
		r = redis.StrictRedis(host=creds['host'], port=creds['port'], password=creds['password'], db=0)
		l = List(redis=r, key='profiles')
		l.append( profile['url'].strip('\n').strip() )
		while len(l) > 20:
			l.pop(0)
	except Exception as e:
		print e
		raise

@app.route('/')
@crossdomain(origin='*')
def keen_chart():
        return app.send_static_file('index.html')

@app.route('/profiles')
@crossdomain(origin='*')
def profiles():
	return app.send_static_file('index.html')

@app.route('/metrics/profiles')
@crossdomain(origin='*')
def profile_data():
	results = []
	try:
	        creds = json.loads(os.environ['VCAP_SERVICES'])['p-redis'][0]['credentials']
	        r = redis.StrictRedis(host=creds['host'], port=creds['port'], password=creds['password'], db=0)
	        l = List(redis=r, key='profiles')
		results = [item for item in l]
	except Exception as e:
		print e
	return json.dumps({'profiles':results}, indent=4)


@app.route('/linkedin/scan', methods=['POST'])
@crossdomain(origin='*')
def post_profile():
        homepage = request.get_json()['homepage']
        print "[profile-scanner] checking homepage: %s" % homepage
        lcard = linkedin.vscrape( url=homepage )
        if lcard.profile:
	        print "[profile-scanner] found user: %s" % lcard.profile
		saveProfile(lcard.vcard)
                return json.dumps(lcard.vcard)
        return json.dumps({})


if __name__ == '__main__':
        print '[twitter-consumer] Waiting for tweets...'
        app.run(host='0.0.0.0', port=int(os.getenv('PORT')) )
