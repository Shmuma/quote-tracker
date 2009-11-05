#!/usr/bin/python

# FX News tracker
import datetime
import httplib
#import json
from google.appengine.ext import db


class News_Record (db.Model):
    id = db.IntegerProperty (required = True)
    lang = db.StringProperty (required = True, choices = ["ru","en"])
    when = db.DateTimeProperty (required = True)
    score = db.IntegerProperty (required = True) # Importance score 0-100
    name = db.StringProperty (required = True)
    country = db.StringProperty (required = True)
    pred = db.StringProperty (required = True)
    fore = db.StringProperty (required = True)
    fact = db.StringProperty (required = False)

    def exists (self):
        q = News_Record.gql ("WHERE id=:1", self.id)
        return len (q.fetch (10)) > 0


def get_calendar_data (date):
    res = None
    conn = httplib.HTTPConnection ("fbs.com")
    try:
        # Warning. fbs has a bug. When we request UTC time, it returns Moscow time. So, we request UTC+1, and remove 1 hour to get UTC.
        req = "/ru/analytics/economic_calendar?action=calendar&day=%d&month=%d&year=%d&country=-1&timezone=1&lang=1&week=1" % (
            date.day, date.month, date.year)
        conn.request ("GET", req)
        r = conn.getresponse ()
        res = r.read ()
    finally:
        conn.close ()
    return res;
    



def process_week (date = None):
    if date == None:
        date = datetime.date.today ()
    
    # Download json data from fbs.com
    data = get_calendar_data (date)
    return data
