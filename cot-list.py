#!/usr/bin/python

import os
from tracker import cot
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache


class CotItemsPage (webapp.RequestHandler):
    def get (self):
        index = 1
        q = db.GqlQuery ("select * from COT_Item order by symbol")

        if self.request.get ("csv"):
            mc_key = "cot_items_csv"
            self.response.headers['Content-Type'] = 'text/plain'
            res = memcache.get (mc_key)
            if res is not None:
                self.response.out.write (res)
            else:
                res = "symbol,last\n"
                for item in q:
                    res += "%s,%s\n" % (item.symbol,item.last.isoformat ());
                self.response.out.write (res);
                # cache output for 1 hour
                memcache.add (mc_key, res, 60*60)
        else:
            res = []
            for item in q:
                item.index = index
                res.append (item)
                index = index + 1
            path = os.path.join (os.path.dirname (__file__), "tmpl/cot-list.html")
            self.response.out.write (template.render (path, {'items': res}))

app = webapp.WSGIApplication ([('/cot-list', CotItemsPage)], debug=True)

def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
