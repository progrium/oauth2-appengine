from oauth.models import OAuth_Token

def oauth_required(scope=None, realm='Example OAuth Service'):
    """ This is a decorator to be used with RequestHandler methods
        that accepts/requires OAuth to access a protected resource
        in accordance with Section 5 of the spec.
        
        If the token is valid, it's passed as a named parameter to 
        the request handler. The request handler is responsible for
        validating the user associated with the token. """
    def decorator(f):
        def wrapped_f(*args):
            request     = args[0].request
            response    = args[0].response
            
            def render_error(error, error_desc, error_uri=None):
                response.set_status({
                    'invalid_request':      400,
                    'invalid_token':        401,
                    'expired_token':        401,
                    'insufficient_scope':   403, }[error])
                authenticate_header = 'OAuth realm="%s", error="%s", error_description="%s"' % \
                    (realm, error, error_desc)
                if error_uri:
                    authenticate_header += ', error_uri="%s"' % error_uri
                if scope:
                    authenticate_header += ', scope="%s"' % scope
                response.headers['WWW-Authenticate'] = authenticate_header
                response.out.write(error_desc)
            
            if request.headers.get('Authorization', '').startswith('OAuth'):
                token = request.headers['Authorization'].split(' ')[1]
            else:
                token = request.get('oauth_token', None)
            
            if not token:
                render_error('invalid_request', "Not a valid request for an OAuth protected resource")
                return
            
            token = OAuth_Token.get_by_access_token(token)
            if token.is_expired():
                if token.refresh_token:
                    render_error('expired_token', "This token has expired")
                else:
                    render_error('invalid_token', "This token is no longer valid")
                return
            
            if scope != token.scope:
                render_error('insufficient_scope', "This resource requires higher priveleges")
                return
            
            f(*args, token=token)
        return wrapped_f
    return decorator
