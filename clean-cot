#!/usr/bin/python

from tracker import cot
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class CleanPage (webapp.RequestHandler):
    def get (self):
        self.response.headers['Content-Type'] = 'text/plain'
        count = 0

        q = cot.COT_Record.all ()
        for rec in q.fetch (500):
            rec.delete ()
            count = count + 1
        self.response.out.write ("Wiped %d records\n" % count)

        q = cot.COT_Last.all ()
        for last in q.fetch (1000):
            last.delete ()

        q = cot.COT_Item.all ()
        for item in q.fetch (1000):
            item.delete ()


app = webapp.WSGIApplication ([('/clean-cot', CleanPage)], debug=True)

def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
