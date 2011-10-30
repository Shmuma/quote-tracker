#!/usr/bin/python

from tracker import utils
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache

from tracker import cot


class COTDataPage (webapp.RequestHandler):
    def get (self, symbol):
        self.response.headers['Content-Type'] = 'text/plain'

        d_from = utils.parseIsoDate (self.request.get ("from"))
        d_to = utils.parseIsoDate (self.request.get ("to"))
        mc_key = "cot_%s_from_%s_to_%s" % (symbol, self.request.get ("from"), self.request.get ("to"))

        res = memcache.get (mc_key);
        if res is not None:
            self.response.out.write (res)
        else:
            cond = ""
            if d_from and d_to:
                q = db.GqlQuery ("select * from COT_Record where symbol = :1 and date >= :2 and date <= :3 order by date asc", symbol, d_from, d_to)
            elif d_from:
                q = db.GqlQuery ("select * from COT_Record where symbol = :1 and date >= :2 order by date asc", symbol, d_from)
            elif d_to:
                q = db.GqlQuery ("select * from COT_Record where symbol = :1 and date <= :2 order by date asc", symbol, d_to)
            else:
                q = db.GqlQuery ("select * from COT_Record where symbol = :1 order by date asc", symbol)
            res = 'Date,OpenInterest,PositionNonCommercialLong,PositionNonCommercialShort,PositionNonCommercialSpread,PositionCommercialLong,PositionCommercialShort,PositionNonRepresentativeLong,PositionNonRepresentativeShort,CountNonCommercialLong,CountNonCommercialShort,CountNonCommercialSpread,CountCommercialLong,CountCommercialShort\n'
            for rec in q:
                res += '%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n' % (rec.date.isoformat (), rec.oi,
                                                                        rec.pos_non_comm_long, rec.pos_non_comm_short, rec.pos_non_comm_spread,
                                                                        rec.pos_comm_long, rec.pos_comm_short,
                                                                        rec.pos_non_rep_long, rec.pos_non_rep_short,
                                                                        rec.count_non_comm_long, rec.count_non_comm_short, rec.count_non_comm_spread,
                                                                        rec.count_comm_long, rec.count_comm_short)
            self.response.out.write (res)
            memcache.add (mc_key, res, 60*60)


app = webapp.WSGIApplication ([('/cot/(.+)', COTDataPage)], debug=True)

def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
