#!/usr/bin/python

from google.appengine.ext import db


class Instrument(db.Model):
    symbol = db.StringProperty (required = True)
    source = db.StringProperty (required = True, choices = ['finam.rts'])
