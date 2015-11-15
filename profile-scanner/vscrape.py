#!/usr/bin/python
import re, requests, urllib2
from bs4 import BeautifulSoup
import urlfetch

class vscrape:

	def __init__(self, url=None):
		self.url = url
		self.profile = None
		self.vcard  = {'fullname':'unknown', 'title':'unknown', 'locality':'unknown', 'industry':'unknown',
                                        'employer':'unknown', 'past':'unknown', 'education':'unknown', 'url':'unknown', 'websites': 'unknown' }

		if self.isLinkedInURL(url=self.url):
			self.vcard['url'] = self.profile
			# uncomment to scrape linkedIn (you might already be blacklisted)
  	        	#self.scrapeProfile(url=self.profile)
        	elif self.scrapeHomepage(url=self.url):
			self.vcard['url'] = self.profile
			# uncomment to scrape linkenIn (you might already be blacklisted)
                	#self.scrapeProfile(url=self.profile)

	def isLinkedInURL(self, url=None):
	        if not url:
        	        return False
        	search1 = re.compile(r"linkedin.com/in")
        	found1 = search1.findall(url)
		search2 = re.compile(r"linkd.in")
		found2 = search2.findall(url)
        	if found1 or found2:
			self.profile = url
                	return True
        	return False


	def scrapeHomepage(self, url=None):
		if not url:
			return False
        	try:
                	#header can be customized
                	HEADER = "Mozilla/5.0 (Macintosh; Intel Mac OSX 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"
                	request = urllib2.Request(url)
                	request.add_header('User-Agent', HEADER)
			request.add_header('Referer', 'https://www.linkedin.com')
                	response = urllib2.urlopen(request)
                	html = response.read()
                	response.close()
                	soup = BeautifulSoup(html)
			for link in soup.find_all('a'):
				link = link.get('href')
				#print 'DEBUG: link in soup: %s' % link
				if self.isLinkedInURL(url=link):
					self.profile = link
					break
        	except Exception as e:
			raise
		finally:
			return self.profile


	def scrapeProfile(self, url=None):
            	try:
                	#header can be customized
                        HEADER = "Mozilla/5.0 (Macintosh; Intel Mac OSX 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"
                    	request = urllib2.Request(url)
                    	request.add_header('User-Agent', HEADER)
			request.add_header('Referer', 'https://www.linkedin.com')
                    	response = urllib2.urlopen(request)
                    	html = response.read()
                    	response.close()
                    	soup = BeautifulSoup(html)

            	except Exception as e:
                	raise

    		vcard = 'undefined'
    		fullname = 'unknown'
    		title = 'unknown'
    		locality = 'unknown'
    		industry = 'unknown'
		employer = 'unknown'
		past = 'unknown'
		education = 'unknown'
		websites = []
            	try:
                	vcard = soup.find("div", {'class':'profile-overview'})
			#print vcard
    		except Exception as e:
			pass
    		try:
    			fullname = soup.find("span", {'class': 'full-name'})
    			fullname = fullname.decode_contents()
            	except Exception as e:
			pass
    		try:
    			title = soup.find("p", {'class': 'title'})
    			title = title.decode_contents()
            	except Exception as e:
			pass
    		try:
    			locality = soup.find("span", {'class': 'locality'})
    			locality = locality.decode_contents()
    		except Exception as e:
			pass
    		try:
    			industry = soup.find("dd", {'class':'industry'})
    			industry = industry.decode_contents()
            	except Exception as e:
			pass
                try:
                        employer = soup.find('tr', {'id': 'overview-summary-current'})
                        employersoup = BeautifulSoup( str(employer) )
                        employer = employersoup.find( 'a', {'dir':'auto'} )
                        employer = employer.decode_contents()
                except Exception as e:
			pass
                try:
                        past = soup.find('tr', {'id': 'overview-summary-past'})
                        pastsoup = BeautifulSoup( str(past) )
                        past = pastsoup.find( 'a', {'dir':'auto'} )
                        past = past.decode_contents()
                except Exception as e:
			pass
                try:
                        edu = soup.find('tr', {'id': 'overview-summary-education'})
                        edusoup = BeautifulSoup( str(edu) )
                        edu = edusoup.find( 'a', {'title': 'More details for this school'} )
                        education = edu.decode_contents()
                except Exception as e:
			pass
                try:
                        web = soup.find('tr', {'id': 'overview-summary-websites'})
                        websoup = BeautifulSoup( str(web) )
			web = websoup.findAll('a')
			for a in web:
				response = requests.get( a.get('href'), allow_redirects=True, verify=False )
				site = response.url.split('url=')[1].split('&')[0]
				site = urllib2.unquote(site).decode('utf8')
				websites.append(site)
                except Exception as e:
			pass
		if not fullname:
			fullname = 'unknown'
		if not title:
	                title = 'unknown'
		if not locality:
	                locality = 'unknown'
		if not industry:
	                industry = 'unknown'
		if not employer:
	                employer = 'unknown'
		if not past:
	                past = 'unknown'
		if not education:
	                education = 'unknown'
		if not websites:
	                websites = ['unknown']

    		self.vcard = {'fullname':fullname, 'title':title, 'locality':locality, 'industry':industry, 
					'employer':employer, 'past':past, 'education':education, 'url':url, 'websites': websites }


