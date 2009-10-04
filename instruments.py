#!/usr/bin/python

from google.appengine.ext import db


class Instrument (db.Model):
    symbol = db.StringProperty (required = True)
    source = db.StringProperty (required = True)
    last_data = db.DateProperty (required = False)

    @classmethod
    def by_symbol (cls, symbol):
        q = Instrument.gql ("where symbol = :1", symbol)
        res = q.fetch (1)
        if len (res):
            return res[0]
        else:
            return None
