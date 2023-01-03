from re import IGNORECASE, fullmatch, match, sub
from base64 import b64decode
from inspect import signature
from .base_auth import RequireAuth
from .exception import *

def doOAuth2TokenAuth(checkerFunc, token_url, **kwargs):
    scope = kwargs['scope'] if 'scope' in kwargs else None
    realm = kwargs['realm'] if 'realm' in kwargs else None
    kwargs['token_url'] = token_url
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
    oAuth2TokenAuth._checker = checkerFunc
    oAuth2TokenAuth._args = kwargs
    return oAuth2TokenAuth

def doOAuth2FormAuth(grant_types=('client_credentials', 'authorization_code', 'password', 'refresh_token')):
    def inner(checkerFunc, **kwargs):
        def oAuth2FormAuth(self, **kwargs):
            self.response['Cache-Control'] = 'no-store'
            if not self.request.form:
                raise INVALID_REQUEST_ERROR(error_description = 'Wrong Content-Type; expecting application/x-www-form-urlencoded')
            if 'grant_type' not in self.request.form or self.request.form['grant_type'] not in grant_types:
                raise UNSUPPORTED_GRANT_TYPE(error_description = 'Unsupported grant_type')
            grant_type = self.request.form['grant_type']
            params = {
                'client_id': self.request.form['client_id'] if 'client_id' in self.request.form else '',
                'client_secret': self.request.form['client_secret'] if 'client_secret' in self.request.form else ''
            }
            if 'Authorization' in self.request.headers and isinstance(self.request.headers['Authorization'], str):
                m = fullmatch('[Bb][Aa][Ss][Ii][Cc] ((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)', self.request.headers['Authorization'])
                if not m:
                    raise INVALID_CLIENT_ERROR(error_description = 'Invalid Client Credentials')
                cred = b64decode(m[1]).decode('utf-8').split(':')
                params['client_id'] = cred[0]
                params['client_secret'] = cred[1]
            if grant_type == 'refresh_token':
                if 'refresh_token' not in self.request.form:
                    raise INVALID_REQUEST_ERROR(error_description =  'Missing refresh_token')
                params['refresh_token'] = self.request.form['refresh_token']
            elif grant_type in ('client_credentials', 'password'):
                params['scope'] = self.request.form['scope'] if 'scope' in self.request.form else ''
                if grant_type == 'password':
                    if 'Authorization' not in self.request.headers and ('username' not in self.request.form or 'password' not in self.request.form):
                        raise INVALID_REQUEST_ERROR(error_description =  'Missing Credentials')
                    params['username'] = self.request.form['username']
                    params['password'] = self.request.form['password']
                elif params['client_id'] == '' or params['client_secret'] == '':
                    raise INVALID_REQUEST_ERROR(error_description =  'Missing Client Credentials')
            elif grant_type == 'authorization_code':
                if 'code' not in self.request.form:
                    raise INVALID_REQUEST_ERROR(error_description =  'Missing Authorization Code')
                params['code'] = self.request.form['code']
                params['redirect_uri'] = self.request.form['redirect_uri'] if 'redirect_uri' in self.request.form else ''
            if not checkerFunc(**{k:v for k,v in params.items() if k in signature(checkerFunc).parameters}):
                raise INVALID_GRANT_ERROR(error_description = 'Invalid Credentials')
            return {k:v for k,v in params.items() if k in ('client_id', 'scope', 'username', 'code', 'redirect_uri')}
        oAuth2FormAuth.__name__ = 'OAuth2Form'
        oAuth2FormAuth._checker = checkerFunc
        oAuth2FormAuth._args = kwargs
        return oAuth2FormAuth
    return inner

RequireOAuth2Token = RequireAuth(doOAuth2TokenAuth)
RequireOAuth2FormAuth = RequireAuth(doOAuth2FormAuth())
RequireOAuth2PasswordAuth = RequireAuth(doOAuth2FormAuth(('password','refresh_token')))
RequireOAuth2CodeAuth = RequireAuth(doOAuth2FormAuth(('authorization_code','refresh_token')))
RequireOAuth2ClientAuth = RequireAuth(doOAuth2FormAuth(('client_credentials','refresh_token')))