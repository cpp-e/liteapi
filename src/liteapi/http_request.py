from inspect import signature
import re, json
from ._internals import _headerDict, _mediaDict, _parse_content_type

def parse_unicode_value(value, charset='utf-8'):
    for m in re.findall('((%[0-9a-fA-F]{2})+)', value):
        value = value.replace(m if m is str else m[0], bytearray.fromhex(m[1:] if m is str else m[0].replace('%', '')).decode(charset.lower()), 1)
    return value

def parse_unicode_fields(name, value):
    if name[-1] != '*':
        return name, value
    res = re.split("'.*'", value)
    return name[:-1], parse_unicode_value(res[1], res[0])

def _getASCIIToDelim(data, delim, startfrom = 0):
        i = data.find(delim, startfrom)
        if i == -1:
            i = len(data)
        value = data[startfrom:i]
        return i + len(delim), value.decode()

def _application_x_www_form_urlencoded(data):
    fs = data.decode().split('&')
    form_data={}
    for f in fs:
        try:
            var, val = f.split('=')
            val = parse_unicode_value(val)
        except:
            var, val = f, None
        var = parse_unicode_value(var)
        isArray = var.find('[]')
        if isArray > 0:
            var = var[:isArray]
            if var not in form_data:
                form_data[var] = []
            form_data[var].append(val)
        else:
            form_data[var] = val
    return form_data

'''
def _multipart_form_data(data):
    boundary = '--' + re.findall('boundary="?([^;$"]+)"?', self.__headers['content-type'])[0] + '\r\n'
    i = 0
    while i < len(data):
        t = data[i:len(boundary)].decode()
        if data[i:len(boundary)].decode() == boundary:
            i += len(boundary)
        i, content_disposition = _getASCIIToDelim(data, b'\r\n', i)
        params = re.findall(r'form-data(?=.*(name)=([^;$]+))(?=.*(filename\*?)=([^;$]+))?.+', content_disposition)
        print (params)
        i += 4
'''

_media_types = _mediaDict({
    'application/x-www-form-urlencoded': {'property': 'form', 'parser': _application_x_www_form_urlencoded},
    'application/json': {'property':'json', 'parser': lambda data, charset = 'utf-8': json.loads(data.decode(charset.lower()))}
})

class http_request:
    def __init__(self, request_data):
        self.__query_str = {}
        self.__json = {}
        self.__form = {}
        self.__obj = {}
        self.__cookies = {}
        self.__protocol = None
        self.__host = None
        self.__port = None

        i, self.__method = _getASCIIToDelim(request_data, b' ')
        i, uri = _getASCIIToDelim(request_data, b' ', i)
        i, self.__version = _getASCIIToDelim(request_data, b'\r\n', i)
        
        headerEnd = request_data.find(b'\r\n\r\n')
        self.__headers = _headerDict()
        while i < headerEnd:
            if request_data[i] in [b' ', b'\t']:
                i, value = _getASCIIToDelim(request_data, b'\r\n', i)
                self.__headers[key] += ('; ' if key.lower() in ['cookie'] else ', ') + value.strip()
            else:
                i, key = _getASCIIToDelim(request_data, b': ', i)
                i, value = _getASCIIToDelim(request_data, b'\r\n', i)
                if key in self.__headers:
                    self.__headers[key] += ('; ' if key.lower() in ['cookie'] else ', ') + value
                else:
                    self.__headers[key] = value
        self.__data = request_data[i+2:]

        hasQuery = uri.find('?')
        self.__base_uri = uri[:hasQuery] if hasQuery > 0 else uri
        self.__uri = uri

        if hasQuery > 0:
            qs = uri[hasQuery+1:].split('&')
            for q in qs:
                try:
                    var, val = q.split('=')
                    val = parse_unicode_value(val)
                except:
                    var, val = q, None
                var = parse_unicode_value(var)
                isArray = var.find('[]')
                if isArray > 0:
                    var = var[:isArray]
                    if var not in self.__query_str:
                        self.__query_str[var] = []
                    self.__query_str[var].append(val)
                else:
                    self.__query_str[var] = val
        
        if 'cookie' in self.__headers:
            self.__cookies = {k:v for k,v in [p.split('=') for p in self.__headers['cookie'].split('; ')]}

    @staticmethod
    def extend_supported_content_types(mimetype, parser_function, override = False, inst_property = 'obj'):
        if not callable(parser_function):
            raise Exception('parser_function must be a callable function')
        if not override and mimetype in _media_types:
            raise Exception(f'mimetype {mimetype} already defined in request mimetypes')
        _media_types[mimetype] = {'parser': parser_function, 'property': inst_property if inst_property in ['obj', 'json', 'form'] else 'obj'}
    
    def parseData(self):
        if not self.__data:
            return
        if 'content-type' not in self.__headers:
            self.__headers['content-type'] = 'application/x-www-form-urlencoded'
        content_type, content_type_params = _parse_content_type(self.__headers['content-type'])
        if content_type in _media_types:
            func = _media_types[content_type]['parser']
            self.__obj = func(self.__data, **{k:v for k,v in content_type_params.items() if k in signature(func).parameters})
            if 'property' in _media_types[content_type] and _media_types[content_type]['property'] != 'obj':
                self.__setattr__(f'_{self.__class__.__name__}__{_media_types[content_type]["property"]}', self.__obj)
    
    @property
    def protocol(self):
        return self.__protocol
    
    @property
    def host(self):
        return self.__headers['host'].split(':')[0] if 'host' in self.__headers else self.__host
    
    @property
    def port(self):
        return int(self.__headers['host'].split(':')[1]) if 'host' in self.__headers and ':' in self.__headers['host'] else self.__port

    @property
    def method(self):
        return self.__method
    
    @property
    def uri(self):
        return self.__uri
    
    @property
    def base_uri(self):
        return self.__base_uri

    @property
    def version(self):
        return self.__version
    
    @property
    def headers(self):
        return self.__headers

    def __getitem__(self, name):
        return self.__headers[name]
    
    def __contains__(self, name):
        return name in self.__headers
    
    def __setitem__(self, name, value):
        self.__headers[name] = value
    
    def __delitem__(self, __key):
        self.__headers.__delitem__(__key)
    
    @property
    def cookies(self):
        return self.__cookies

    @property
    def data(self):
        return self.__data
    
    @property
    def json(self):
        return self.__json
    
    @property
    def obj(self):
        return self.__obj
    
    @property
    def form(self):
        return self.__form

    @property
    def query_string(self):
        return self.__query_str
