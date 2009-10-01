from google.appengine.api import memcache
from cacher import *


class SettingsProvider (Provider):
    def set (self, val):
        """
        Here we must save settings value hash to DataStore
        """

    def get (self):
        """
        Load settings dictionary from DataStore
        """
        return {}



def getSettingsCacher ():
    return Cacher (SettingsProvider (), "settings", 0)
