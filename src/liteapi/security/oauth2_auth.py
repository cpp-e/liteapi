from re import IGNORECASE, fullmatch, match
from base64 import b64decode
from inspect import signature
from .base_auth import RequireAuth
from .exception import *

def doOAuth2TokenAuth(checkerFunc, **kwargs):
    scope = kwargs['scope'] if 'scope' in kwargs else None
    realm = kwargs['realm'] if 'realm' in kwargs else None
    def oAuth2TokenAuth(self, **kwargs):
        self.response['Cache-Control'] = 'no-store'
        params = {}
        if realm:
            params['realm'] = realm
        if scope:
            params['scope'] = scope
        if ('Authorization' not in self.request.headers \
            or not match('Bearer', self.request.headers['Authorization'], IGNORECASE)) \
            and 'access_token' not in self.request.form \
            and 'access_token' not in self.request.query_string:
            raise TOKEN_ERROR(**params)
        if ('Authorization' in self.request.headers \
            and ('access_token' in self.request.form or 'access_token'in self.request.query_string)) \
            or ('access_token' in self.request.form and 'access_token'in self.request.query_string):
            raise INVALID_REQUEST_ERROR(error_description='access_token received using multiple methods')
        params['access_token'] = self.request.headers['Authorization'][self.request.headers['Authorization'].rfind(' ')+1:] if 'Authorization' in self.request.headers else self.request.form['access_token'] if 'access_token' in self.request.form else self.request.query_string['access_token']
        if not checkerFunc(**{k:v for k,v in params.items() if k in signature(checkerFunc).parameters}):
            raise INVALID_TOKEN_ERROR(**params)
        return params
    oAuth2TokenAuth.__name__ = 'OAuth2'
    return oAuth2TokenAuth

def doOAuth2PassAuth(checkerFunc, **kwargs):
    def oAuth2PassAuth(self, **kwargs):
        self.response['Cache-Control'] = 'no-store'
        if not self.request.form:
            raise INVALID_REQUEST_ERROR(error_description = 'Wrong Content-Type; expecting application/x-www-form-urlencoded')
        if 'grant_type' not in self.request.form or self.request.form['grant_type'] != 'password':
            raise UNSUPPORTED_GRANT_TYPE(error_description = 'Unknown grant_type')
        if 'Authorization' not in self.request.headers and ('username' not in self.request.form or 'password' not in self.request.form):
            raise INVALID_REQUEST_ERROR(error_description =  'Missing Credentials')
        params = {
            'client_id': self.request.form['client_id'] if 'client_id' in self.request.form else '',
            'client_secret': self.request.form['client_secret'] if 'client_secret' in self.request.form else '',
            'scope': self.request.form['scope'] if 'scope' in self.request.form else '',
            'username': self.request.form['username'],
            'password': self.request.form['password']
        }
        if 'Authorization' in self.request.headers and isinstance(self.request.headers['Authorization'], str):
            m = fullmatch('Basic ((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)', self.request.headers['Authorization'])
            if not m:
                raise INVALID_CLIENT_ERROR(error_description = 'Invalid Client Credentials')
            cred = b64decode(m[1]).decode('utf-8').split(':')
            params['client_id'] = cred[0]
            params['client_secret'] = cred[1]
        if not checkerFunc(**{k:v for k,v in params.items() if k in signature(checkerFunc).parameters}):
            raise INVALID_GRANT_ERROR(error_description = 'Invalid Credentials')
        return {k:v for k,v in params.items() if k in ('client_id', 'scope', 'username')}
    oAuth2PassAuth.__name__ = 'OAuth2'
    return oAuth2PassAuth

RequireOAuth2Token = RequireAuth(doOAuth2TokenAuth)
RequireOAuth2PasswordAuth = RequireAuth(doOAuth2PassAuth)