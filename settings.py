from google.appengine.ext import db
from cacher import *


class Setting (db.Model):
    val = db.StringProperty (required = True)


class SettingsProvider (Provider):
    def set (self, val):
        """
        Here we must save settings value hash to DataStore
        """
        s = Setting (val)
        s.put ()

    def get (self):
        """
        Load settings dictionary from DataStore
        """
        s = db.GqlQuery ("select * from Setting")
        if length (s) > 0:
            return s[0]
        else:
            return self.defaults ()

    def defaults (self):
        s = {}
        s['max_fetch_interval'] = 0
        return s


def getSettingsCacher ():
    return Cacher (SettingsProvider (), "settings", 0)
