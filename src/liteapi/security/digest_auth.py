from hashlib import md5, sha256, sha512
from secrets import token_urlsafe
from re import findall
from inspect import signature
from .base_auth import RequireAuth
from ..http_request import parse_unicode_fields
from ..exception import UNAUTHORIZED_ERROR

ALGORITHMS = {
    'MD5': md5,
    'MD5-sess': md5,
    'SHA-256': sha256,
    'SHA-256-sess': sha256,
    'SHA-512-256': sha512,
    'SHA-512-256-sess': sha512
}

def calc_ha1(**kwargs):
    if 'algorithm' not in kwargs \
    or 'username' not in kwargs \
    or 'realm' not in kwargs \
    or 'password' not in kwargs \
    or ('-sess' in kwargs['algorithm'] and 'cnonce' not in kwargs) \
    or 'nonce' not in kwargs:
        return
    hash = ALGORITHMS[kwargs['algorithm']]
    ha1 = hash('{}:{}:{}'.format(kwargs['username'], kwargs['realm'], kwargs['password']).encode()).hexdigest()
    if '-sess' in kwargs['algorithm']:
        ha1 = hash('{}:{}:{}'.format(ha1, kwargs['nonce'], kwargs['cnonce']).encode()).hexdigest()
    return ha1

def digest(**kwargs):
    if 'algorithm' not in kwargs \
    or 'ha1' not in kwargs \
    and ('username' not in kwargs \
    or 'realm' not in kwargs \
    or 'password' not in kwargs) \
    or ('-sess' in kwargs['algorithm'] and 'cnonce' not in kwargs) \
    or 'nonce' not in kwargs \
    or 'uri' not in kwargs \
    or 'method' not in kwargs \
    or ('qop' in kwargs and ('nc' not in kwargs or 'cnonce' not in kwargs)):
        return
    
    hash = ALGORITHMS[kwargs['algorithm']]
    
    ha1 = kwargs['ha1'] if 'ha1' in kwargs else calc_ha1(**{k:v for k,v in kwargs.items() if k in ('algorithm', 'username', 'realm', 'password', 'nonce', 'cnonce')})

    ha2 = hash('{}:{}'.format(kwargs['method'], kwargs['uri']).encode()).hexdigest()
    response = None
    response = hash('{}:{}:'.format(ha1, kwargs['nonce']).encode())
    if('qop' in kwargs):
        response.update('{}:{}:{}:'.format(kwargs['nc'], kwargs['cnonce'], kwargs['qop']).encode())
    response.update(ha2.encode())
    return response.hexdigest()

def doDigestAuth(method, checkerFunc, **kwargs):
    AUTH_SCHEME='Digest'
    options = ' algorithm={}'.format(kwargs['algorithm'] if 'algorithm' in kwargs else 'MD5')
    options += ', realm="{}"'.format(kwargs['realm']) if 'realm' in kwargs else ''
    options += ', domain="{}"'.format(kwargs['domain']) if 'domain' in kwargs else ''
    options += ', qop="{}"'.format(kwargs['qop']) if 'qop' in kwargs else ''
    options += ', opaque="{}"'.format(kwargs['opaque']) if 'opaque' in kwargs else ''
    nonce_handle = kwargs['nonce_handle'] if 'nonce_handle' in kwargs else token_urlsafe
    def inner(self, **kwargs):
        auth_options = options
        if 'Authorization' not in self.request.headers:
            auth_options += ', nonce="{}"'.format(nonce_handle())
            raise UNAUTHORIZED_ERROR({'WWW-Authenticate': '{}{}'.format(AUTH_SCHEME, auth_options)})
        ms = None
        if isinstance(self.request.headers['Authorization'], str):
            ms = findall(r'Digest (?=.*\b(username\*?)\b=([^,$]+))(?=.*\b(realm)\b=([^,$]+))?(?=.*\b(uri)\b=([^,$]+))(?=.*\b(algorithm)\b=([^,$]+))(?=.*\b(nonce)\b=([^,$]+))(?=.*\b(nc)\b=([^,$]+))?(?=.*\b(cnonce)\b=([^,$]+))?(?=.*\b(qop)\b=([^,$]+))?(?=.*\b(response)\b=([^,$]+))(?=.*\b(opaque)\b=([^,$]+))?.+', self.request.headers['Authorization'])
        if not ms:
            auth_options += ', nonce="{}"'.format(nonce_handle())
            raise UNAUTHORIZED_ERROR({'WWW-Authenticate': '{}{}'.format(AUTH_SCHEME, auth_options)})
        params = {
            'method': self.request.method
        }
        for i in range(0, len(ms[0]), 2):
            if ms[0][i]:
                name, val = parse_unicode_fields(ms[0][i], ms[0][i + 1].strip('"'))
                params[name] = val
        params['digest_password'] = lambda password: digest(password=password, **params)
        params['digest_ha1'] = lambda ha1: digest(ha1=ha1, **params)
        if not checkerFunc(**{k:v for k,v in params.items() if k in signature(checkerFunc).parameters}):
            auth_options += ', nonce="{}"'.format(nonce_handle())
            raise UNAUTHORIZED_ERROR({'WWW-Authenticate': '{}{}'.format(AUTH_SCHEME, auth_options)})
        return method(self, **kwargs, **{k:v for k,v in {'username': params['username']}.items() if k in signature(method).parameters})
    return inner

RequireDigestAuth = RequireAuth(doDigestAuth)