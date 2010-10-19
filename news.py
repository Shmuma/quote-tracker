#!/usr/bin/python

# FX News tracker
import datetime
import httplib
from google.appengine.ext import db


class News_Record_v2 (db.Model):
    when = db.DateTimeProperty (required = True)
    # Importance 0 = low, 1 = medium, 2 = high
    importance = db.IntegerProperty (required = True)
    title = db.StringProperty (required = True)
    curr = db.StringProperty (required = False)
    pred = db.StringProperty (required = False)
    fore = db.StringProperty (required = False)


def record_exists (record):
    q = News_Record_v2.gql ("WHERE when = :1 and title = :2", record.when, record.title)
    res = q.fetch (1)
    if len (res) > 0:
        return res[0]
    else:
        return None


def get_calendar_data (date):
    res = None
    # http://www.dailyfx.com/files/Calendar-10-17-2010.csv
    conn = httplib.HTTPConnection ("www.dailyfx.com")
    try:
        req = "/files/Calendar-%02d-%02d-%d.csv" % (date.month, date.day, date.year)
        conn.request ("GET", req)
        r = conn.getresponse ()
        res = r.read ().decode ("utf-8")
    finally:
        conn.close ()
    return res;


def imp2val (imp):
    imp = imp.lower ()
    if imp == 'high':
        return 2
    elif imp == 'medium':
        return 1
    else:
        return 0


def val2imp (val):
    if val == 2:
        return 'high'
    elif val == 1:
        return 'medium'
    else:
        return 'low'


# if date is not specified, fetch upcoming week
def fetch_week (date = None):
    if date == None:
        date = datetime.date.today ()
    # we round date to next sunday
    while date.weekday () != 6:
        date += datetime.timedelta (days = 1)

    data = get_calendar_data (date)
    if data == None:
        return []
    res = []
    for record in data.split ("\n")[1:]:
        val = record.split (",")
        if len (val) < 9:
            continue
        d = int (val[0].split (" ")[2])
        while date.day != d:
            date += datetime.timedelta (days = 1)
        when = datetime.datetime (date.year, date.month, date.day)
        t = val[1].split (":")
        if len (t) > 1:
            when = when.replace (hour = int (t[0]), minute = int (t[1]))
        res.append (News_Record_v2 (when = when, importance = imp2val (val[5]), title = val[4], curr = val[3], pred = val[8], fore = val[7]))
    return res
