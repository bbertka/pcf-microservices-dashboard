#!/usr/bin/python

from flask import Flask, request, redirect, url_for, send_from_directory, make_response, current_app
from functools import update_wrapper
from datetime import timedelta
import json, os, logging
import cfworker
import analysis

BUBBLE_STATS = analysis.bubblestats()
PIE_STATS = analysis.piestats()
TIMELINE = analysis.timeline()

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

#---------------------------------------------------------------
#
# app routes: end points for the app's web interfaces
#
#---------------------------------------------------------------
worker = cfworker.cfworker( port=int(os.getenv('PORT')) )
worker.app = Flask(__name__, static_url_path='')

@worker.app.route('/')
@crossdomain(origin='*')
def keen_chart():
        return worker.app.send_static_file('index.html')

@worker.app.route('/bubbles')
@crossdomain(origin='*')
def bubble_chart():
        return worker.app.send_static_file('bubbles.html')

@worker.app.route('/sentiment')
@crossdomain(origin='*')
def pie_chart():
        return worker.app.send_static_file('sentiment.html')

@worker.app.route('/timeline')
@crossdomain(origin='*')
def timeline_chart():
        return worker.app.send_static_file('timeline.html')

@worker.app.route('/metrics/timeline')
@crossdomain(origin='*')
def timeline_data():
        global TIMELINE
        return json.dumps({'timeline': TIMELINE.tweets})

@worker.app.route('/timeline/post', methods=['POST'])
@crossdomain(origin='*')
def post_timeline():
	global TIMELINE
	try:
		tweet = request.get_json()['tweet']
		TIMELINE.update(tweet=tweet)
	except Exception as e:
		print e
	finally:
		return json.dumps(TIMELINE.tweets)

@worker.app.route('/bubbles/post', methods=['POST'])
@crossdomain(origin='*')
def post_bubbles():
        global BUBBLE_STATS
        try:
                trends = [str(f).lower() for f in request.get_json()['trends'] ]
                BUBBLE_STATS.update( trends=trends )
        except Exception as e:
                print e
        finally:
                return json.dumps( BUBBLE_STATS.trend_count )

@worker.app.route('/metrics/field-value-counters/hashtags')
@crossdomain(origin='*')
def metric_counter():
        global BUBBLE_STATS
        url = 'http://0.0.0.0:%d/metrics/field-value-counters/hashtags' % int(os.getenv('PORT'))
        return json.dumps({"name":"hashtags","links":[{"rel":"self","href": url}],"counts": BUBBLE_STATS.trend_count })

@worker.app.route('/pie/post', methods=['POST'])
@crossdomain(origin='*')
def post_pie():
        global PIE_STATS
        try:
                sentiment = [request.get_json()['sentiment'] ]
                PIE_STATS.update( sentiment=sentiment )
                print PIE_STATS.sentiment_count
        except Exception as e:
                print e
        finally:
                return json.dumps( PIE_STATS.sentiment_count )

@worker.app.route('/metrics/field-value-counters/sentiment')
@crossdomain(origin='*')
def pie_metric_counter():
        global PIE_STATS
        url = 'http://0.0.0.0:%d/metrics/field-value-counters/sentiment' % int(os.getenv('PORT'))
        return json.dumps({"name":"sentiment","links":[{"rel":"self","href": url}],"counts": PIE_STATS.sentiment_count })


@worker.app.route('/metrics/field-value-counters')
@crossdomain(origin='*')
def field_counter():
        return ""

#---------------------------------------------------------------
#
# logging: suppresses some of the annoying Flask output
#
#---------------------------------------------------------------
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)
