================
browsercookiejar
================
.. image:: https://badge.fury.io/py/browsercookiejar.svg
    :target: http://badge.fury.io/py/browsercookiejar

`browsercookiejar` is a Python CookieJar set for Chrome, Firefox and MSIE.

Requirements
============
* pycrypto for Chrome on Linux

Setup
=====
::

    $ pip install browsercookiejar

Usage
=====
Run this code, logging in to Google on Chrome::

    import re
    import urllib2
    import browsercookiejar

    cj = browsercookiejar.ChromeCookieJar()
    cj.load()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    body = opener.open('http://www.google.com').read()
    account = re.search(r'>([^>]+@gmail\.com)', body).group(1)

    print 'Your account is', account
