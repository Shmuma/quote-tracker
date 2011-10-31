from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from tracker import myfx

import pprint


class MyFXFetchCommunity (webapp.RequestHandler):
    def get (self):
        cred = myfx.MyFXLoginCredentials ()
        if not cred.valid:
            self.response.out.write ('We have no credentials, exit')
        else:
            outlook = myfx.MyFXCommunityOutlook (cred.token)
            if outlook.get ():
                pp = pprint.PrettyPrinter ()
                self.response.out.write ('Outlook: %s' % pp.pformat (outlook.data))
            else:
                self.response.out.write ('Outlook fetch failure')


app = webapp.WSGIApplication ([('/myfx-fetch-comm', MyFXFetchCommunity)], debug=True)


def main ():
    run_wsgi_app (app)

if __name__ == "__main__":
    main ()
