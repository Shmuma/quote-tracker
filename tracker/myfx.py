import urllib2

import os.path
import cPickle as pickle
import json


from google.appengine.ext import db



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
        fd = urllib2.urlopen (url)
        data = fd.read ()
        fd.close ()

        data = json.JsonReader ().read (data)
        if data['error']:
            return False

        MyFXToken (login = name, token = data['session']).put ()
        return True
