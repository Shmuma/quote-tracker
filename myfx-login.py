#!/usr/bin/python

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import os

from tracker import myfx


class MyFXBookLogin (webapp.RequestHandler):
    def get (self):
        self.response.headers['Content-Type'] = 'text/plain'

        login = self.request.get ('login', default_value=None)
        paswd = self.request.get ('password', default_value=None)
        if login and paswd:
            if myfx.MyFXLoginCredentials.authorize (login, paswd):
                s = "Login OK, token saved\n"
            else:
                s = "Login failed\n"
        else:
            if self.request.get ('check', default_value=None):
                cred = myfx.MyFXLoginCredentials ()
                if cred.valid ():
                    s = "We have token for %s" % cred.login
                else:
                    s = "We have no token"
            else:
                s = "Required arguments not specified. You must provide both login and password."
        self.response.out.write (s)



app = webapp.WSGIApplication ([('/myfx-login', MyFXBookLogin)], debug=True)


def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
    
