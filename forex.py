import httplib
import json


# We use webcharts.fxserver.com for quote source.

# Available periods table:
# M1 = 0
# M5 = 1
# M10 = 2
# M15 = 3
# M30 = 4
# H1 = 5
# H2 = 6
# H4 = 7
# D1 = 8
# W1 = 9
# M1 = 10


class FXFetcher:
    periods = {
        'H1': {'arg': 5, 'interval': 3600},
        'H4': {'arg': 7, 'interval': 14400},
        'D1': {'arg': 8, 'interval': 86400},
        }

    def __init__ (self):
        self.conn = httplib.HTTPConnection ("webcharts.fxserver.com")
        self.req_url = "/charts/activeChartFeed.php?pair=%(pair1)s/%(pair2)s&period=%(period)d&unit=&limit=%(bars)d&timeout=0&rateType=bid&GMT=off"

    def fetch (self, pair1, pair2, period, bars):
        try:
            do_req = self.req_url % { 'pair1': pair1, 'pair2': pair2, 
                                      'period': FXFetcher.periods[period]["arg"],
                                      'bars': bars}
            self.conn.request ("GET", do_req)
            r = self.conn.getresponse ()
            if r.status == 200:
                return json.read (r.read ())['candles']
            else:
                return None
        except:
            return None

    def close (self):
        self.conn.close ()
