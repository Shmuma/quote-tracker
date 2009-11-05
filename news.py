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

    def exists (self):
        q = News_Record.gql ("WHERE id=:1", self.id)
        return len (q.fetch (10)) > 0


def get_calendar_data (date):
    res = None
    conn = httplib.HTTPConnection ("fbs.com")
    try:
        # Warning: fbs has a bug. When we request UTC time, it returns Moscow time. So, we request UTC+1, and remove 1 hour to get UTC.
        req = "/ru/analytics/economic_calendar?action=calendar&day=%d&month=%d&year=%d&country=-1&timezone=1&lang=1&week=1" % (
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
    return datetime.datetime.today ()



def fetch_week (date = None):
    if date == None:
        date = datetime.date.today ()
    
    # Download json data from fbs.com
    data = get_calendar_data (date)
    if data == None:
        return []
    count = 0
    res = []
    rus = {}
    for obj in json.read (data):
        if obj['siteId'] == '2':
            res.append (News_Record (id = int (obj['id']), when = parse_date_time (obj['date'], obj['time']), 
                                     score = 0, name = obj['index'].encode ('utf-8'),
                                     country = obj['country'], 
                                     pred = filter_str (obj['pred']),
                                     fore = filter_str (obj['forecast']),
                                     fact = filter_str (obj['fact']),
                                     curr = None));
        else:
            rus[int (obj['id'])] = obj['index'].encode ('utf-8')
        count = count + 1

    # update name_ru field of according objects
    for obj in res:
        if (obj.id+1 in rus) and (rus[obj.id+1].find (obj.name) == 0):
            r = rus[obj.id + 1].split (' - ')
            obj.name_ru = r[1]
        elif (obj.id-1 in rus) and (rus[obj.id-1].find (obj.name) == 0):
            r = rus[obj.id - 1].split (' - ')
            obj.name_ru = r[1]
    return res
