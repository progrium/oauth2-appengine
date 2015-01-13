from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template, util
from google.appengine.api import users
from django.utils import simplejson

import urllib

from oauth.models import OAuth_Authorization, OAuth_Token, OAuth_Client

def extract(keys, d):
    """ Extracts subset of a dict into new dict """
    return dict((k, d[k]) for k in keys if k in d)

class AuthorizationHandler(webapp.RequestHandler):
    SUPPORTED_RESPONSE_TYPES = [
        'code',
        'token',
        'code_and_token', ] # NOTE: code_and_token may be removed in spec
    
    def authz_redirect(self, query, fragment=None):
        query_string    = ('?%s' % urllib.urlencode(query))     if query else ''
        fragment_string = ('#%s' % urllib.urlencode(fragment))  if fragment else ''
        self.redirect(''.join([self.redirect_uri, query_string, fragment_string]))
    
    def authz_error(self, code, description=None):
        error = {'error': code, 'error_description': description}
        if self.request.get('state'):
            error['state'] = self.request.get('state')
        self.authz_redirect(error)

    def validate_params(self):
        self.user = users.get_current_user()
        if self.request.method == 'POST' and not self.user:
            self.error(403)
            self.response.out.write("Authentication required.")
            return False
        
        self.redirect_uri = self.request.get('redirect_uri')
        if not self.redirect_uri:
            self.error(400)
            self.response.out.write("The parameter redirect_uri is required.")
            return False
        # TODO: validate url?
        
        if not self.request.get('response_type') in self.SUPPORTED_RESPONSE_TYPES:
            self.authz_error('unsupported_response_type', "The requested response type is not supported.")
            return False
        
        self.client = OAuth_Client.get_by_client_id(self.request.get('client_id'))
        if not self.client:
            self.authz_error('invalid_client', "The client identifier provided is invalid.")
            return False
        
        if self.client.redirect_uri:
            if self.client.redirect_uri != self.redirect_uri:
                self.authz_error('redirect_uri_mismatch', 
                    "The redirection URI provided does not match a pre-registered value.")
                return False
        
        return True

    @util.login_required
    def get(self):
        # TODO: put scope into ui
        if not self.validate_params():
            return
        template_data = extract([
            'response_type',
            'redirect_uri',
            'client_id',
            'scope',
            'state',], self.request.GET)
        template_data['client'] = self.client
        self.response.out.write(
            template.render('templates/authorize.html', template_data))
    
    def post(self):
        if not self.validate_params():
            return
        
        # TODO: check for some sort of cross site request forgery? sign the request?
        
        if self.request.get('authorize').lower() == 'no':
            self.authz_error('access_denied', "The user did not allow authorization.")
            return
        
        response_type = self.request.get('response_type')
        
        if response_type in ['code', 'code_and_token']:
            code = OAuth_Authorization(
                user_id         = self.user.user_id(),
                client_id       = self.client.client_id,
                redirect_uri    = self.redirect_uri, )
            code.put()
            code = code.serialize(state=self.request.get('state'))
        else:
            code = None
        
        if response_type in ['token', 'code_and_token']:
            token = OAuth_Token(
                user_id     = self.user.user_id(),
                client_id   = self.client.client_id,
                scope       = self.request.get('scope'), )
            token.put(can_refresh=False)
            token = token.serialize(requested_scope=self.request.get('scope'))
        else:
            token = None
        
        self.authz_redirect(code, token)
        


class AccessTokenHandler(webapp.RequestHandler):
    SUPPORTED_GRANT_TYPES = [
        'client_credentials', 
        'refresh_token', 
        'authorization_code', 
        'password',
        #'none', (will require not giving refresh token)  ... == client_credentials?
        #'assertion', (will require not giving refresh token)
        ]
    
    def render_error(self, code, description):
        self.error(400)
        self.response.headers['content-type'] = 'application/json'
        self.response.out.write(simplejson.dumps(
            {'error': code, 'error_description': description,}))
    
    def render_response(self, token):
        self.response.headers['content-type'] = 'application/json'
        self.response.out.write(simplejson.dumps(
            token.serialize(requested_scope=self.request.get('scope'))))
    
    def get(self):
        """ This method MAY be supported according to spec """
        self.handle()
    
    def post(self):
        """ This method MUST be supported according to spec """
        self.handle()
    
    def handle(self):
        # TODO: MUST require transport-level security
        client_id       = self.request.get('client_id')
        client_secret   = self.request.get('client_secret')
        grant_type      = self.request.get('grant_type')
        scope           = self.request.get('scope')
        
        if not grant_type in self.SUPPORTED_GRANT_TYPES:
            self.render_error('unsupported_grant_type', "Grant type not supported.")
            return
        
        client = OAuth_Client.authenticate(client_id, client_secret)
        if not client:
            self.render_error('invalid_client', "Inavlid client credentials.")
            return

        # Dispatch to one of the grant handlers below
        getattr(self, 'handle_%s' % grant_type)(client, scope)
    
    def handle_password(self, client, scope=None):
        # Since App Engine doesn't let you programmatically auth,
        # and the local SDK environment doesn't need a password,
        # we just always grant this w/out auth
        # TODO: something better?
        
        username = self.request.get('username')
        password = self.request.get('password')
        
        if not username or not password:
            self.render_error('invalid_grant', "Invalid end-user credentials.")
            return
        
        token = OAuth_Token(
            client_id   = client.client_id, 
            user_id     = username, 
            scope       = scope, )
        token.put()
        
        self.render_response(token)
    
    def handle_client_credentials(self, client, scope=None):
        token = OAuth_Token(
            client_id   = client.client_id, 
            scope       = scope, )
        token.put(can_refresh=False)
        
        self.render_response(token)
        
    def handle_refresh_token(self, client, scope=None):
        token = OAuth_Token.get_by_refresh_token(self.request.get('refresh_token'))
        
        if not token or token.client_id != client.client_id:
            self.render_error('invalid_grant', "Invalid refresh token.")
            return
            
        # TODO: refresh token should expire along with grant according to spec
        token = token.refresh()
        
        self.render_response(token)
            
    def handle_authorization_code(self, client, scope=None):
        authorization   = OAuth_Authorization.get_by_code(self.request.get('code'))
        redirect_uri    = self.request.get('redirect_url')
        
        if not authorization or not authorization.validate(code, redirect_uri, client.client_id):
            self.render_error('invalid_grant', "Authorization code expired or invalid.")
            return
        
        token = OAuth_Token(
            user_id     = authorization.user_id,
            client_id   = authorization.client_id,
            scope       = scope, )
        token.put()
        authorization.delete()
        
        self.render_response(token)

