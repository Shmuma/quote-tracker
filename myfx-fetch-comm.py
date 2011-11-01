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
                sample = myfx.MyFXCommunitySample.fetch (cred.token)
                self.response.out.write ('Outlook: %s\n' % sample)
                sample.out = self.response.out;
                if sample.isFresh ():
                    self.response.out.write ('Data is fresh')
                else:
                    self.response.out.write ('Data is the same as before')
                sample.updateCache ()
            except:
                self.response.out.write ('Outlook fetch failure')
                raise


app = webapp.WSGIApplication ([('/myfx-fetch-comm', MyFXFetchCommunity)], debug=True)


def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
