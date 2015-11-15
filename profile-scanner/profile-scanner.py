#!/usr/bin/python
import json, os, random, time
from flask import Flask, request, redirect, url_for, send_from_directory
import vscrape as linkedin
import redis
from redis_collections import List

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
def keen_chart():
        return app.send_static_file('index.html')

@app.route('/profiles')
def profiles():
	return app.send_static_file('index.html')

@app.route('/metrics/profiles')
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
