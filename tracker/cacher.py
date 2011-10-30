#!/usr/bin/python

from google.appengine.api import memcache


class Provider:
    def get (self):
        raise NotImplementedError

    def set (self, value):
        raise NotImplementedError


class Cacher:
    """
    Class caches one value in memcache. It works as a wrap around special provider class with two
    methods: get and set. Cache is write-through.
    """

    def __init__(self, prov, key, timeout = 0):
        """
        Initialize cacher
        """
        self.__key = key
        self.__prov = prov
        self.__timeout = timeout
        self.__val = None


    def get (self):
        """
        Obtain value
        """
        if self.__val == None:
            val = memcache.get (self.__key)
            if val == None:
                val = self.__prov.get ()
                memcache.set (self.__key, val, 0, self.__timeout)
            self.__val = val
        return self.__val


    def set (self, val):
        """
        Changes value
        """
        self.__prov.set (val)
        memcache.set (self.__key, val, 0, self.__timeout)
        self.__val = val
