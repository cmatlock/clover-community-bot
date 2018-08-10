# pylint: disable=missing-docstring

import sys
sys.path.append("lib")

import requests
from requests_toolbelt.adapters import appengine
import webapp2
import config

import daily_digest
import hottest

appengine.monkeypatch()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

APP = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/daily_digest', daily_digest.DailyDigest),
    ('/hottest', hottest.Hottest),
], debug=True)
