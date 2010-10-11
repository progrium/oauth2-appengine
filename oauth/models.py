from google.appengine.ext import db
import time
import hashlib
import random

def now():
    return int(time.mktime(time.gmtime()))

def random_str():
    return hashlib.sha1(str(random.random())).hexdigest()

class OAuth_Token(db.Model):
    EXPIRY_TIME = 3600*24
    
    user_id         = db.StringProperty()
    client_id       = db.StringProperty()
    access_token    = db.StringProperty()
    refresh_token   = db.StringProperty(required=False)
    scope           = db.StringProperty(required=False)
    expires         = db.IntegerProperty(required=False)
    
    @classmethod
    def get_by_refresh_token(cls, refresh_token):
        return cls.all().filter('refresh_token =', refresh_token).get()
    
    @classmethod
    def get_by_access_token(cls, access_token):
        return cls.all().filter('access_token =', access_token).get()
    
    def put(self, can_refresh=True):
        if can_refresh:
            self.refresh_token  = random_str()
        self.access_token       = random_str()
        self.expires            = now() + self.EXPIRY_TIME
        super(OAuth_Token, self).put()
    
    def refresh(self):
        if not self.refresh_token:
            return None # Raise exception?
            
        token = OAuth_Token(
            client_id   = self.client_id, 
            user_id     = self.user_id,
            scope       = self.scope, )
        token.put()
        self.delete()
        return token
    
    def is_expired(self):
        return self.expires < now()
    
    def serialize(self, requested_scope=None):
        token = dict(
            access_token        = self.access_token,
            expires_in          = self.expires - now(), )
        if (self.scope and not requested_scope) \
            or (requested_scope and self.scope != requested_scope):
            token['scope']      = self.scope
        if self.refresh_token:
            token['refresh_token'] = self.refresh_token
        return token


class OAuth_Authorization(db.Model):
    EXPIRY_TIME = 3600
    
    user_id         = db.StringProperty()
    client_id       = db.StringProperty()
    code            = db.StringProperty()
    redirect_uri    = db.StringProperty()
    expires         = db.IntegerProperty()
    
    @classmethod
    def get_by_code(cls, code):
        return cls.all().filter('code =', code).get()
    
    def put(self):
        self.code       = random_str()
        self.expires    = now() + self.EXPIRY_TIME
        super(OAuth_Authorization, self).put()
    
    def is_expired(self):
        return self.expires < now()
    
    def validate(self, code, redirect_uri, client_id=None):
        valid = not self.is_expired() \
            and self.code == code \
            and self.redirect_uri == redirect_uri
        if client_id:
            valid &= self.client_id == client_id
        return valid
    
    def serialize(self, state=None):
        authz = {'code': self.code}
        if state:
            authz['state'] = state
        return authz



class OAuth_Client(db.Model):
    client_id       = db.StringProperty()
    client_secret   = db.StringProperty()
    redirect_uri    = db.StringProperty()
    
    # This is not necessary according to spec,
    # however, effectively you need it for UX
    name            = db.StringProperty()

    @classmethod
    def get_by_client_id(cls, client_id):
        return cls.all().filter('client_id =', client_id).get()
    
    @classmethod
    def authenticate(cls, client_id, client_secret):
        client = cls.get_by_client_id(client_id)
        if client and client.client_secret == client_secret:
            return client
        else:
            return None
    
    def put(self):
        self.client_id      = random_str()
        self.client_secret  = random_str()
        super(OAuth_Client, self).put()
