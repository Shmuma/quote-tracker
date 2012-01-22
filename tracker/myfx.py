import os.path
import cPickle as pickle
import json
import datetime
import zlib

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
        data = urlfetch.fetch (url, headers = {'Cache-Control': 'max-age=30'}).content
        return MyFXCommunitySample (datetime.datetime.utcnow (), json.JsonReader ().read (data))


    @staticmethod
    def _csvTopLevelFields ():
        """
        Fields from top-level json to be displayed in CSV
        """
        return ['dateTime']


    @staticmethod
    def _csvGeneralFields ():
        """
        Returns a list with fields needed from 'general' section of data hash
        """
        return ['totalFunds', 'fundsWon', 'fundsLost',
                'realAccountsPercentage', 'profitablePercentage', 'nonProfitablePercentage',
                'demoAccountsPercentage', 
                'averageDeposit', 'averageAccountProfit', 'averageAccountLoss']


    @staticmethod
    def _csvSymbolFields ():
        """
        Returns a list with fields needed for each symbol
        """
        return ['longPositions', 'shortPositions', 'totalPositions',
                'longVolume', 'shortVolume',
                'longPercentage', 'shortPercentage',
                'avgLongPrice', 'avgShortPrice']


    @staticmethod
    def symbols ():
        """
        Returns a list of symbols names
        """
        return ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD',
                'USDCHF', 'GBPJPY', 'EURJPY', 'EURCHF', 'EURGBP']


    @staticmethod
    def csvHeaderString ():
        """
        Return a string with CSV header
        """
        syms = []
        fields = MyFXCommunitySample._csvSymbolFields ()
        for s in MyFXCommunitySample.symbols ():
            syms += map (lambda name: "%s_%s" % (s, name), fields)
        return ';'.join (MyFXCommunitySample._csvTopLevelFields () +
                         MyFXCommunitySample._csvGeneralFields () + syms)


    def csvString (self):
        """
        Return a CSV representation of a sample
        """
        def decomma (s):
            return str (s).replace (',', '')

        res = []
        for k in MyFXCommunitySample._csvTopLevelFields ():
            if k == 'dateTime':
                res.append ("%s" % self.dt)
            else:
                res.append (decomma (self.data.get (k, '')))

        general = self.data.get ('general', {})
        for k in MyFXCommunitySample._csvGeneralFields ():
            res.append (decomma (general.get (k, '')))
        
        symbols = {}
        for item in self.data.get ('symbols', []):
            symbols[item['name']] = item
        
        for sym in MyFXCommunitySample.symbols ():
            data = symbols.get (sym, {})
            for k in MyFXCommunitySample._csvSymbolFields ():
                res.append (decomma (data.get (k, '')))

        return ';'.join (res)



class MyFXCommunityData (db.Model):
    """
    Data with MyFXBook community outlook data.
    Each data object holds data array for one day.
    """
    date = db.DateProperty (required = True)
    entries = db.BlobProperty (required = True)


    @staticmethod
    def get_entries (date = None, limit = 1000):
        """
        Obtain list of entries objects for the given date value
        """
        q = MyFXCommunityData.all ()
        if date != None:
            q.filter ("date = ", date)
        entries = []
        for val in q.fetch (limit):
            entries += pickle.loads (zlib.decompress (val.entries))
        return entries


    @staticmethod
    def append (date, sample):
        q = MyFXCommunityData.all ()
        q.filter ("date = ", date)
        data = q.fetch (1)
        if len (data) > 0:
            data = data[0]
            entries = pickle.loads (zlib.decompress (data.entries))
            entries.append (sample)
            data.entries = zlib.compress (pickle.dumps (entries))
        else:
            entries = []
            data = MyFXCommunityData (date = date, entries = zlib.compress (pickle.dumps ([sample])))
        data.put ()
