import re
import urllib2
import browsercookiejar

cj = browsercookiejar.ChromeCookieJar()
cj.load()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
body = opener.open('http://www.google.com').read()
account = re.search(r'>([^>]+@gmail\.com)', body).group(1)

print 'Your account is', account
