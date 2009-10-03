#!/usr/bin/python

import datetime
import httplib
from google.appengine.ext import db


class Quote (db.Model):
    date = db.DateProperty (required = True)
    open = db.FloatProperty (required = True)
    high = db.FloatProperty (required = True)
    low = db.FloatProperty (required = True)
    close = db.FloatProperty (required = True)
    volume = db.IntegerProperty (required = True)


def sourceInstance (source):
    """
    Instantiates correct class
    """
    if source == 'yahoo':
        return YahooSource ()
    elif source == 'finam.rts':
        return FinamSource ()
    else:
        return None


class Source:
    def fetch (symbol, start, finish = datetime.date.today ()):
        """
        fetches symbol's quotes and return array of quote object
        """
        return None



# http://ichart.finance.yahoo.com/table.csv?s=MSFT&d=9&e=3&f=2009&g=d&a=2&b=13&c=1986&ignore=.csv
class YahooSource (Source):
    def fetch (self, symbol, start, finish = datetime.date.today ()):
        req = '/table.csv?s=%(sym)s&d=%(to_m)d&e=%(to_d)d&f=%(to_y)d&g=d&a=%(from_m)d&b=%(from_d)d&c=%(from_y)d&ignore=.csv' % {
            'sym' : symbol,
            'to_m' : finish.month - 1,
            'to_d' : finish.day,
            'to_y' : finish.year,
            'from_m' : start.month - 1,
            'from_d' : start.day,
            'from_y' : start.year }
        conn = httplib.HTTPConnection ("ichart.finance.yahoo.com")
        conn.request ("GET", req)
        r = conn.getresponse ()
        res = r.read ()
        conn.close ()
        return res


class FinamSource (Source):
    pass
