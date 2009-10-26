#!/usr/bin/python

import datetime

def parseIsoDate (str):
    """
    Converts string of format YYYY-MM-DD to datetime object
    """
    d = str.split ("-")
    if len (d) != 3:
        return None
    return datetime.date (int (d[0]), int (d[1]), int (d[2]))
