from webtest import TestApp
from main import application, ProtectedResourceHandler
from oauth.models import OAuth_Client
from google.appengine.api import apiproxy_stub_map, datastore_file_stub

app = TestApp(application())

# clear datastore
apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map['datastore_v3'].Clear()

# set up test client
client = OAuth_Client(name='test')
client.put()

def test_protected_resource_fail_naked():
    response = app.get('/protected/resource', status=400)
    assert not ProtectedResourceHandler.SECRET_PAYLOAD in str(response)

def test_protected_resource_success_flow():
    response = app.post('/oauth/token', dict(
        grant_type = 'password',
        username = 'user',
        password = 'pass',
        client_id = client.client_id,
        client_secret = client.client_secret,
        scope = 'read',
    ))
    assert 'access_token' in response.json.keys()
    token = response.json['access_token']
    response = app.get('/protected/resource', dict(oauth_token=token))
    assert ProtectedResourceHandler.SECRET_PAYLOAD in str(response)