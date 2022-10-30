from datetime import date, datetime, time
from inspect import signature
import json
import re
from .APIModel import APIJSONEncoder, APIModel, _repr
from ._internals import _mediaDict, _headerDict, _parse_content_type, _is_valid_token, _is_valid_cookie_value_octet, _is_valid_cookie_path

def _application_json(data, charset = 'utf-8'):
    ret = ''
    if type(data) in [int, float, bool, str]:
        ret = json.dumps({'data': data})
    elif type(data) in [list, tuple, dict] or issubclass(type(data), APIModel):
        ret = json.dumps(data, cls=APIJSONEncoder)
    else:
        raise Exception(f'Unsupported response data: returned type {_repr(data)}')
    return ret.encode(charset)

_response_media_types = _mediaDict({
    'application/json': _application_json,
    'text/*': lambda data, charset = 'utf-8': f'{data}'.encode(charset)
})

class _cookies:
    def __init__(self, name, value, expires = None, max_age = None, path = None, domain = None, secure = False, httponly = False):
        if not isinstance(name, str) and not _is_valid_token(name):
            raise Exception(f'Cannot set cookie name to "{name}"; name cannot contain CTL characters or separators')

        self.__name = name
        self.value = value
        self.expires = expires
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.httponly = httponly
    
    @property
    def name(self):
        return self.__name
    
    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if not isinstance(value, str):
            raise Exception(f'Cannot set the value of cookie "{self.__name}" to "{value}"')
        self.__value = ''
        for c in value:
            if not _is_valid_cookie_value_octet(c) or ord(c) > 0x7F:
                self.__value += ''.join(f'%{b:02x}' for b in c.encode())
            else:
                self.__value += c
        
    @property
    def expires(self):
        return self.__expires
    
    @expires.setter
    def expires(self, expires):
        if expires.__class__ is date:
            expires = datetime.combine(expires, time())
        elif expires.__class__ is time:
            expires = datetime.combine(date.today(), expires)
        elif expires and not isinstance(expires, datetime):
            raise Exception(f'Invalid Expires value for cookie "{self.__name}"; expect datetime, date, or time type')
        self.__expires = expires

    @property
    def max_age(self):
        return self.__max_age
    
    @max_age.setter
    def max_age(self, max_age):
        if max_age and not isinstance(max_age, int):
            raise Exception(f'Invalid Max-Age value for cookie "{self.__name}"')
        self.__max_age = max_age


    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, path):
        if path and (not isinstance(path, str) or not _is_valid_cookie_path(path)):
            raise Exception(f'Invalid Path value for cookie "{self.__name}"')
        self.__path = path if '__Host-' not in self.__name else '/'
    
    @property
    def domain(self):
        return self.__domain
    
    @domain.setter
    def domain(self, domain):
        if domain and not re.fullmatch('[a-zA-Z][a-zA-Z0-9\-]*(?:\.[a-zA-Z][a-zA-Z0-9\-]*)*', domain):
            raise Exception(f'Invalid Domain value for cookie "{self.__name}"')
        self.__domain = domain if '__Host-' not in self.__name else None
    
    @property
    def secure(self):
        return self.__secure
    
    @secure.setter
    def secure(self, secure):
        if not isinstance(secure, bool):
            raise Exception(f'Invalid Secure value for cookie "{self.__name}; expect boolean value"')
        self.__secure = secure if '__Secure-' not in self.__name and '__Host-' not in self.__name else True

    @property
    def httponly(self):
        return self.__httponly

    @httponly.setter
    def httponly(self, httponly):
        if not isinstance(httponly, bool):
            raise Exception(f'Invalid HttpOnly value for cookie "{self.__name}; expect boolean value"')
        self.__httponly = httponly

    def __str__(self):
        _str = f'{self.__name}={self.__value}'
        if self.__expires:
            _str += f'; Expires={self.__expires.strftime("%a, %d %b %Y %H:%M:%S %Z")}'
        if self.__max_age:
            _str += f'; Max-Age={self.__max_age}'
        if self.__path:
            _str += f'; Path={self.__path}'
        if self.__domain:
            _str += f'; Domain={self.__domain}'
        if self.__secure:
            _str += f'; Secure'
        if self.__httponly:
            _str += f'; HttpOnly'
        return _str

class http_response:
    def __init__(self):
        self.__cookies = {}
        self.__headers = _headerDict()
    
    @staticmethod
    def extend_supported_content_types(mimetype, parser_function, override = False):
        if not callable(parser_function):
            raise Exception('parser_function must be a callable function')
        if not override and mimetype in _response_media_types:
            raise Exception(f'mimetype {mimetype} already defined in response mimetypes')
        _response_media_types[mimetype] = parser_function

    @property
    def cookies(self):
        return self.__cookies

    @property
    def headers(self):
        return self.__headers

    def __contains__(self, name):
        return name in self.__headers
    
    def __setitem__(self, name, value):
        self.__headers[name] = value
    
    def __delitem__(self, __key):
        self.__headers.__delitem__(__key)
    
    def getResponse(self, data):
        if 'content-type' not in self.__headers:
            self.__headers['content-type'] = 'application/json; charset=utf-8'
        content_type, content_type_params = _parse_content_type(self.__headers['content-type'])
        if content_type in _response_media_types:
            func = _response_media_types[content_type]
            return func(data, **{k:v for k,v in content_type_params.items() if k in signature(func).parameters})
        return f'{data}'.encode()

    def setCookies(self, name, value, expires = None, max_age = None, path = None, domain = None, secure = False, httponly = False):
        self.__cookies[name] = _cookies(name, value, expires, max_age, path, domain, secure, httponly)

    @property
    def responseHeader(self):
        header = ""
        for key in self.__headers:
            if isinstance(self.__headers[key], str):
                header += f'{key}: {self.__headers[key]}\r\n'
            else:
                for val in self.__headers[key]:
                    header += f'{key}: {val}\r\n'
        for cookie in self.__cookies:
            header += f'Set-Cookie: {self.__cookies[cookie]}\r\n'
        return header