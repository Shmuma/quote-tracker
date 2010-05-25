#!/usr/bin/python

# FX News tracker
import datetime
import httplib
import json
from google.appengine.ext import db


class News_Record (db.Model):
    id = db.IntegerProperty (required = True)
    when = db.DateTimeProperty (required = True)
    # Importance score 0-100
    score = db.IntegerProperty (required = True)
    name = db.StringProperty (required = True)
    name_ru = db.StringProperty (required = False)
    country = db.StringProperty (required = False)
    pred = db.StringProperty (required = False)
    fore = db.StringProperty (required = False)
    fact = db.StringProperty (required = False)
    # Comma-separated list of currencies that can be affected. None if it will potentially affect all FX market.
    curr = db.StringProperty (required = False)


def lookup_news_record (id):
    q = News_Record.gql ("WHERE id=:1", id)
    res = q.fetch (10)
    if len (res) > 0:
        return res[0]
    else:
        return None


def get_calendar_data (date):
    res = None
    conn = httplib.HTTPConnection ("fbs.com")
    try:
        # Warning: fbs has a bug. When we request UTC time, it returns Moscow time. So, we request UTC+1, and remove 1 hour to get UTC.
        req = "/ru/analytics/economic_calendar?action=calendar&day=%d&month=%d&year=%d&country=-1&timezone=1&lang=2&week=1" % (
            date.day, date.month, date.year)
        conn.request ("GET", req)
        r = conn.getresponse ()
        res = r.read ()
    finally:
        conn.close ()
    return res;



def filter_str (str):
    if str == '-':
        return None
    else:
        return str



def parse_date_time (date, time):
    d = date.split ("-")
    t = time.split (":")
    return datetime.datetime (int (d[0]), int (d[1]), int (d[2]), int (t[0]), int (t[1])) - datetime.timedelta (hours = 1)



def country_to_currency (country):
    h = {"New Zealand" : "NZD",
         "Australia" : "AUD",
         "Japan" : "JPY",
         "China" : None,
         "Britain" : "GBP",
         "USA": "USD",
         "EU": "EUR",
         "France" : "EUR",
         "Italy" : "EUR",
         "Germany" : "EUR",
         "Canada" : "CAD"}
    if country in h:
        return h[country]
    else:
        return None


# Estimate importance score values for object
def score (obj):
    return 0



def fetch_week (date = None):
    if date == None:
        date = datetime.date.today ()

    # Download json data from fbs.com
    data = get_calendar_data (date)
    if data == None:
        return []
    count = 0
    res = []
    for obj in json.read (data):
        res.append (News_Record (id = int (obj['id']), when = parse_date_time (obj['date'], obj['time']),
                                 score = 0, name = obj['index'],
                                 country = obj['country'],
                                 pred = filter_str (obj['pred']),
                                 fore = filter_str (obj['forecast']),
                                 fact = filter_str (obj['fact']),
                                 curr = country_to_currency (obj['country'])));
        count = count + 1
    return res
