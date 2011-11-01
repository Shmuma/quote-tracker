import os.path
import cPickle as pickle
import json
import datetime

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.api import memcache


class MyFXToken (db.Model):
    login = db.StringProperty (required = True)
    token = db.StringProperty (required = True)




class MyFXLoginCredentials (object):
    """
    Incapsulates login auth token.
    """
    
    def __init__ (self):
        self._load_creds ()

    
    def _load_creds (self):
        self.login = None
        self.token = None
        for tok in MyFXToken.all ().fetch (limit = 1):
            self.login = tok.login
            self.token = tok.token


    def valid (self):
        """
        Returns true if credentals exists.
        """
        return self.login != None and self.token != None


    @staticmethod
    def authorize (name, password):
        """
        Performs login to MyFXBook server to obtain token. Saves name and token
        for future usage (password won't be saved). Returns True if login
        successfull, False if an error occured.
        """
        url = "https://www.myfxbook.com/api/login.json?email=%s&password=%s" % (name, password)
        data = urlfetch.fetch (url).content

        data = json.JsonReader ().read (data)
        if data['error']:
            return False

        MyFXToken (login = name, token = data['session']).put ()
        return True



class MyFXCommunitySample (object):
    """
    Represents single unique sample of community outlook data. Daily samples are
    stores into single blob in MyFXCommunityDay for storage efficiency.
    """
    last_data_key = "MyFXCommunitySample_last"

    def __init__ (self, dt, json_data):
        """
        Initialize comunity sample object from json: http://www.myfxbook.com/api
        """
        if json_data['error']:
            raise ValueError
        self.dt = dt
        self.data = json_data


    def __str__ (self):
        return "<MyFXCommunitySample: %s, data = %s>" % (self.dt, self.data)


    def isFresh (self):
        """
        Obtains previously stored sample's data from memcache and compares it with own data.
        """
        data = memcache.get (key = MyFXCommunitySample.last_data_key)
        if data == None:
            return True
        dat = pickle.loads (data)
        return dat != self.data


    def updateCache (self):
        """
        Puts data in memcache.
        """
        memcache.set (key = MyFXCommunitySample.last_data_key, value = pickle.dumps (self.data))


    @staticmethod
    def fetch (token):
        """
        Constructs sample object by fetching myfxbook.
        """
        url = "http://www.myfxbook.com/api/get-community-outlook.json?session=%s" % token
        data = urlfetch.fetch (url, headers = {'Cache-Control': 'max-age=60'}).content
        return MyFXCommunitySample (datetime.datetime.utcnow (), json.JsonReader ().read (data))


class MyFXCommunityData (db.Model):
    """
    Data with MyFXBook community outlook data.
    Each data object holds data array for one day.
    """
    date = db.DateProperty (required = True)
    entries = db.BlobProperty (required = True)

    @staticmethod
    def append (date, sample):
        pass
