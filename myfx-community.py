import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from tracker import myfx


class MyFXFetchCommunity (webapp.RequestHandler):
    def get (self):
        cred = myfx.MyFXLoginCredentials ()
        if not cred.valid:
            self.response.out.write ('We have no credentials, exit')
        else:
            try:
                # obtain new sample from myfx
                sample = myfx.MyFXCommunitySample.fetch (cred.token)
                # if sample is fresh, append it into current date's blob
                if sample.isFresh () or self.request.get ('skipcache', default_value=False):
                    sample.updateCache ()
                    myfx.MyFXCommunityData.append (datetime.datetime.utcnow ().date (), sample)
                    self.response.out.write ('Data appended')
                else:
                    self.response.out.write ('Not appended, because of duplicate')
            except:
                self.response.out.write ('Outlook fetch failure')
                raise


class MyFXCommunity (webapp.RequestHandler):
    def get (self):
        self.response.out.write ('Hello, World!')



app = webapp.WSGIApplication ([('/myfx-fetch-comm', MyFXFetchCommunity),
                               ('/myfx-community', MyFXCommunity)], debug=True)


def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
