from re import fullmatch
from base64 import b64decode
from inspect import signature
from .base_auth import RequireAuth
from ..exception import UNAUTHORIZED_ERROR

def doBasicAuth(checkerFunc, **kwargs):
    AUTH_SCHEME='Basic'
    realm = ' realm="{}"'.format(kwargs['realm']) if 'realm' in kwargs else ''
    def basicAuth(self, **kwargs):
        if 'Authorization' not in self.request.headers:
            raise UNAUTHORIZED_ERROR({'WWW-Authenticate': '{}{}'.format(AUTH_SCHEME, realm)})
        m = None
        if isinstance(self.request.headers['Authorization'], str):
            m = fullmatch('[Bb][Aa][Ss][Ii][Cc] ((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)', self.request.headers['Authorization'])
        if not m:
            raise UNAUTHORIZED_ERROR({'WWW-Authenticate': '{}{}'.format(AUTH_SCHEME, realm)})
        cred = b64decode(m[1]).decode('utf-8').split(':')
        params = {
            'username': cred[0],
            'password': cred[1]
        }
        if not checkerFunc(**{k:v for k,v in params.items() if k in signature(checkerFunc).parameters}):
            raise UNAUTHORIZED_ERROR({'WWW-Authenticate': '{}{}'.format(AUTH_SCHEME, realm)})
        return {'username': cred[0]}
    basicAuth.__name__ = 'basic'
    basicAuth._checker = checkerFunc
    basicAuth._args = kwargs
    return basicAuth

RequireBasicAuth = RequireAuth(doBasicAuth)