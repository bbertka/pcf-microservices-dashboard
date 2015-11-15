#!/usr/bin/python
import requests, json, os, sys
from textblob import TextBlob
from collections import Counter


def computeSentiment(data):
	""" Quick and Dirty Sentiment """
	value = 'Neutral'
	sentiment = TextBlob(data['text']).sentiment.polarity
	if sentiment < 0:
		value = 'Bad'
	elif sentiment > 0:
		value = 'Good'
	return value

def sendToBubbles(data):
        try:
                hashtags = [ tag['text'].encode('utf-8').lower() for tag in data['entities']['hashtags'] ]
                if hashtags:
                        r = requests.post(url='http://0.0.0.0:%d/bubbles/post' % int(os.getenv('PORT')),
                                data=json.dumps({'trends': hashtags }), headers={'Content-Type': 'application/json'})
        except Exception as e:
                print 'Analysis error, found a problem parsing hashtag list: %s' % e

def sendToPie(data):
        try:
		sentiment = computeSentiment(data)
                r = requests.post(url='http://0.0.0.0:%d/pie/post' % int(os.getenv('PORT')),
                        data=json.dumps({'sentiment': sentiment }), headers={'Content-Type': 'application/json'})
        except Exception as e:
                print 'Analysis error, found a problem parsing sentiment: %s' % e

def sendToTimeline(data):
	try:
		created = data['created_at'].split('+')[0].strip().split(' ')
		short = created[0]+'-'+created[1]+'-'+created[2]
		user = "@"+data['user']['screen_name']
		url = ''
		text = data['text']+' '+url
		image = data['user']['profile_image_url']
		if text.split(' @')[0]=='RT':
			user = text.strip('RT').split(':')[0]
			text = text.split(':')[1]
			image = data['retweeted_status']['user']['profile_image_url']
			if data['retweeted_status']['entities']['urls']:
				url = data['retweeted_status']['entities']['urls'][0]['url']
		homepage = 'https://twitter.com/%s' % user.split('@')[1]
		tweet = {'user': user, 'homepage': homepage, 'text': text, 'url':url, 'user_image': image}
		r = requests.post(url='http://0.0.0.0:%d/timeline/post' % int(os.getenv('PORT')), 
			data=json.dumps({'tweet': tweet }), headers={'Content-Type': 'application/json'})
	except Exception as e:
		print 'Analysis error, found a problem parsing tweet data: %s' % e


def populate(data):
	sendToBubbles(data)
	sendToPie(data)
	sendToTimeline(data)


#---------------------------------------------------------------
#
# stats: keeps track of the tag counts
#
#---------------------------------------------------------------
class bubblestats:
        def __init__(self):
                self.trend_raw = []
                self.trend_count = Counter()
        def update(self, trends=[]):
                # this keeps track of the size of the bubble chart
                if len(self.trend_raw) >= int( os.getenv('MAX_CHART_SIZE') ):
                        self.trend_raw = []
                        self.trend_count = Counter()
                else:
                        self.trend_raw.extend(trends)
                        self.trend_count = Counter( self.trend_raw )
                        top20 = self.trend_count.most_common(20)
                        self.trend_raw = []
                        for tag, num in top20:
                            for i in range(0, num):
                                self.trend_raw.append(tag)
                        self.trend_count = Counter( self.trend_raw )

        def add(self, trends=[]):
                # this lets the bubble chart grow bigger
                self.trend_count = Counter(trends) + self.trend_count


class timeline:
	def __init__(self):
		self.tweets = list()
	def update(self, tweet=None):
		if tweet:
			self.tweets.append(tweet)
		if len(self.tweets) > 10:
			self.tweets.pop(0)

class piestats:
        def __init__(self):
                self.sentiment_raw = ['Good', 'Bad', 'Neutral']
                self.sentiment_count = Counter()

        def update(self, sentiment=[]):
                # this keeps track of the size of the pie chart (grows to sys MAXINT size)
                if len(self.sentiment_raw) >= int( os.getenv('MAX_CHART_SIZE') ):
                        self.sentiment_raw = ['Good', 'Bad', 'Neutral']
                        self.sentiment_count = Counter()
                else:
                        self.sentiment_raw.extend(sentiment)
                        self.sentiment_count = Counter( self.sentiment_raw )
                        self.sentiment_count.most_common()
        def add(self, sentiment=[]):
                self.sentiment_count = Counter(sentiment) + self.sentiment_count
