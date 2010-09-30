from google.appengine.ext import webapp, db
from django.utils import simplejson

from google.appengine.ext.webapp import util, template
from google.appengine.api import users
import urllib

from oauth.handlers import AuthorizationHandler, AccessTokenHandler
from oauth.models import OAuth_Client

# Notes:
# Access tokens usually live shorter than access grant
# Refresh tokens usually live as long as access grant


class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

class ClientsHandler(webapp.RequestHandler):
    """ This is only indirectly necessary since the spec
        calls for clients, but managing them is out of scope 
        """
    
    def get(self):
        clients = OAuth_Client.all()
        self.response.out.write(
            template.render('templates/clients.html', locals()))
    
    def post(self):
        client = OAuth_Client(
            name            = self.request.get('name'),
            redirect_uri    = self.request.get('redirect_uri'), )
        client.put()
        self.redirect(self.request.path)


def main():
    application = webapp.WSGIApplication([
        ('/',                   MainHandler),
        ('/oauth/authorize',    AuthorizationHandler),
        ('/oauth/token',        AccessTokenHandler),
        ('/app/clients',        ClientsHandler),    ],debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
