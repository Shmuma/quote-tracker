#!/usr/bin/python

import datetime
import httplib
from google.appengine.ext import db


class Quote (db.Model):
    symbol = db.StringProperty (required = True)
    date = db.DateProperty (required = True)
    open = db.FloatProperty (required = True)
    high = db.FloatProperty (required = True)
    low = db.FloatProperty (required = True)
    close = db.FloatProperty (required = True)
    volume = db.IntegerProperty (required = True)
    period = db.StringProperty (required = False, choices = ['day', 'week', 'month'])


def sourceInstance (source):
    """
    Instantiates correct class
    """
    if source == 'yahoo':
        return YahooSource ()
    elif source == 'finam.rts':
        return FinamSource ()
    elif source == 'rbc.micex':
        return RBCMicexSource ()
    else:
        return None


def parseIsoDate (str):
    """
    Converts string of format YYYY-MM-DD to datetime object
    """
    d = str.split ("-")
    return datetime.date (int (d[0]), int (d[1]), int (d[2]))




class Source:
    def minDate (self):
        """
        Minimal date for fetch
        """
        return datetime.date (1970, 1, 1)

    def fetchSimple (self, symbol, start):
        return self.fetch (symbol, start, datetime.date.today ())

    def fetch (self, symbol, start, finish):
        """
        fetches symbol's quotes and return array of quote object
        """
        return None


class CsvHttpSource (Source):
    def getRequest (self, symbol, start, finish):
        return None

    def getServer (self, symbol):
        return None

    def line2quote (self, symbol, arr):
        return None

    def needReverse (self):
        return False

    def fetch (self, symbol, start, finish):
        result = []
        try:
            req = self.getRequest (symbol, start, finish)
            conn = httplib.HTTPConnection (self.getServer (symbol))
            conn.request ("GET", req)
            r = conn.getresponse ()
            res = r.read ()
            conn.close ()
            lines = res.split ("\n")
            if self.needReverse ():
                lines.reverse ()
            for l in lines:
                if l == '':
                    continue
                res = self.line2quote (symbol, l.split (','))
                if res != None:
                    result.append (res)
        except:
            pass
        return result


# http://ichart.finance.yahoo.com/table.csv?s=MSFT&d=9&e=3&f=2009&g=d&a=2&b=13&c=1986&ignore=.csv
class YahooSource (CsvHttpSource):
    def minDate (self):
        """
        Minimal date for fetch
        """
        return datetime.date (1800, 1, 1)

    def getRequest (self, symbol, start, finish):
        return '/table.csv?s=%(sym)s&d=%(to_m)d&e=%(to_d)d&f=%(to_y)d&g=%(period)s&a=%(from_m)d&b=%(from_d)d&c=%(from_y)d&ignore=.csv' % {
            'sym' : symbol,
            'to_m' : finish.month - 1,
            'to_d' : finish.day,
            'to_y' : finish.year,
            'from_m' : start.month - 1,
            'from_d' : start.day,
            'from_y' : start.year,
            'period' : 'd'}

    def getServer (self, symbol):
        return 'ichart.finance.yahoo.com'

    def needReverse (self):
        return True

    def line2quote (self, symbol, arr):
        if arr[0] == 'Date' or len (arr) != 7:
            return None
        if arr[1] == '' or arr[2] == '' or arr[3] == '' or arr[4] == '':
            return None
        return Quote (symbol = symbol,
                      date = parseIsoDate (arr[0]),
                      open = float (arr[1]),
                      high = float (arr[2]),
                      low  = float (arr[3]),
                      close = float (arr[4]),
                      volume = long (arr[5]))


class FinamSource (Source):
    pass


# http://export.rbc.ru/expdocs/free.micex.0.shtml
# http://export.rbc.ru/free/micex.0/free.fcgi?period=DAILY&tickers=AVAZ&d1=04&m1=10&y1=1990&d2=04&m2=10&y2=2009&separator=%2C&data_format=BROWSER&header=1
class RBCMicexSource (CsvHttpSource):
    def getRequest (self, symbol, start, finish):
        return '/free/micex.0/free.fcgi?period=DAILY&tickers=%(sym)s&d1=%(f_d)d&m1=%(f_m)d&y1=%(f_y)d&d2=%(t_d)d&m2=%(t_m)d&y2=%(t_y)d&separator=%%2C&data_format=BROWSER&header=1' % {
            'sym' : symbol,
            'f_d' : start.day,
            'f_m' : start.month,
            'f_y' : start.year,
            't_d' : finish.day,
            't_m' : finish.month,
            't_y' : finish.year,
            }

    def getServer (self, symbol):
        return 'export.rbc.ru'

    def line2quote (self, symbol, arr):
        if len (arr) != 8 or arr[0] == 'TICKER':
            return None
        if arr[2] == '' or arr[3] == '' or arr[4] == '' or arr[5] == '':
            return None
        return Quote (symbol = symbol,
                      date = parseIsoDate (arr[1]),
                      open = float (arr[2]),
                      close = float (arr[5]),
                      high = float (arr[3]),
                      low = float (arr[4]),
                      volume = long (arr[6]))
