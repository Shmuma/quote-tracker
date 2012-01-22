import datetime
import os.path

from google.appengine.dist import use_library
use_library('django', '0.96')

from google.appengine.ext.webapp import template
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
        # if no options passed, display usage help and exit
        try:
            d = datetime.datetime.strptime (self.request.get ('date', ''), '%Y-%m-%d')
        except ValueError:
            self.show_help ()
            return

        self.response.headers['Content-Type'] = 'text/csv'
        self.response.headers['Content-Disposition'] = 'filename=myfx-community-%s.csv' % self.request.get ('date', '')
        self.response.out.write (myfx.MyFXCommunitySample.csvHeaderString () + '\n')
        
        for entry in myfx.MyFXCommunityData.get_entries (d):
            self.response.out.write (entry.csvString () + '\n')


    def show_help (self):
        """
        Displays template with usage help
        """
        path = os.path.join (os.path.dirname (__file__), "tmpl/myfx-community-help.html")
        self.response.out.write (template.render (path, {}))


app = webapp.WSGIApplication ([('/myfx-fetch-comm', MyFXFetchCommunity),
                               ('/myfx-community', MyFXCommunity)], debug=True)


def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
