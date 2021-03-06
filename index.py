#!/usr/bin/python

import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db


class MainPage (webapp.RequestHandler):
    def get (self):
        args = {}
        path = os.path.join (os.path.dirname (__file__), "tmpl/index.html")
        self.response.out.write (template.render (path, args))



app = webapp.WSGIApplication ([('/', MainPage)], debug=True)


def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
