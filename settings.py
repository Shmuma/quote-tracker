from google.appengine.api import memcache


class SettingsError:
    def __init__ (self, msg):
        self.message = msg


class SettingsStore:
    """
    Interface to persistent application settings
    They are stored in DataStore and cached using memcache.
    """
    __mc_key = "settings"
    __dict = {}
    __dirty = False

    def __init__ (self):
        """
        Initialize default values and trying to load settings
        """
        self.__dict["quote_refresh_interval"] = 120
        self.load ()


    def set (self, key, val):
        """
        Assigns value to setting
        """
        if key in self.__dict:
            if self.__dict[key] != val:
                self.__dict[key] = val
                self.__dirty = True
        else:
            self.__dict[key] = val
            self.__dirty = True


    def get (self, key):
        """
        Obtains value from settings store. Returns None if no such option exists.
        """
        if key in self.__dict:
            return self.__dict[key]
        else:
            return None


    def load (self):
        """
        Loads settings from store. First tries to read from memcache.  If memcache is missing, load
        from data store. In that case, we cache values in memcache.

        Return true if load succeed, or false otherwise
        """
        vals = memcache.get (self.__mc_key)
        if vals == None:
            vals = self.__load_ds ()
            if vals == None:
                return False
            memcache.set (self.__mc_key, vals)
        self.__dict = vals;
        return True


    def save (self):
        """
        Saves settings and returns True on success. If store not modified, return True,
        but no actual save performed to minimise DS and memcache requests.
        """
        if not self.__dirty:
            return True
        # update DS
        if not self.__save_ds ():
            return False
        # update memcache
        memcache.set (self.__mc_key, self.__dict)
        self.__dirty = False;


    def __load_ds (self):
        """
        Load settings from DataStore. Returns values hash on success of None at error
        """
        return None


    def __save_ds (self):
        """
        Save settings to DataStore. Returns True or False.
        """
        return True
