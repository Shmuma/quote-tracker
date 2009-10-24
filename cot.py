#!/usr/bin/python

# Commitment of Traders (http://www.cftc.gov) data handling

from google.appengine.ext import db
import csv
import httplib
import datetime
from cacher import *


class COT_Record (db.Model):
    # GOLD, EUR, MEAT, etc
    symbol = db.StringProperty (required = True)
    date = db.DateProperty (required = True)
    # Open Interest
    oi = db.IntegerProperty (required = True)
    # Non Commercial
    pos_non_comm_long = db.IntegerProperty (required = True)
    pos_non_comm_short = db.IntegerProperty (required = True)
    pos_non_comm_spread = db.IntegerProperty (required = True)
    # Commercial
    pos_comm_long = db.IntegerProperty (required = True)
    pos_comm_short = db.IntegerProperty (required = True)
    # Non reportable
    pos_non_rep_long = db.IntegerProperty (required = True)
    pos_non_rep_short = db.IntegerProperty (required = True)
    # count of traders
    count_non_comm = db.IntegerProperty (required = True)
    count_comm = db.IntegerProperty (required = True)
    count_non_rep = db.IntegerProperty (required = True)

class COT_Last (db.Model):
    date = db.DateProperty (required = True)


class COT_Last_Provider:
    def get (self):
        # download http://cftc.gov/dea/newcot/deacit.txt, and check first line and fird CSV value
        try:
            conn = httplib.HTTPConnection ("www.cftc.gov")
            conn.request ("GET", "/dea/newcot/deacit.txt")
            r = conn.getresponse ()
            res = r.read ()
            conn.close ()
            for row in csv.reader ([res.split ('\n')[0]], delimiter=',', quotechar='"'):
                if row[2] == '':
                    return None
                d = row[2].split ("-")
                return datetime.date (int (d[0]), int (d[1]), int (d[2]))           
        except:
            pass
        return None
        


def last_cot_report_date ():
    """
    Return date of latest COT report. If report cannot be downloaded, return None
    """
    return Cacher (COT_Last_Provider (), "last_cot", 60*60).get ()

