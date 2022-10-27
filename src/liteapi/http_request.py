from inspect import signature
import re, json

def parse_unicode_value(value, charset='utf-8'):
    for m in re.findall('((%[0-9a-fA-F]{2})+)', value):
        value = value.replace(m if m is str else m[0], bytearray.fromhex(m[1:] if m is str else m[0].replace('%', '')).decode(charset.lower()), 1)
    return value

def parse_unicode_fields(name, value):
    if name[-1] != '*':
        return name, value
    res = re.split("'.*'", value)
    return name[:-1], parse_unicode_value(res[1], res[0])

def __getASCIIToDelim(data, delim, startfrom = 0):
        i = data.find(delim, startfrom)
        if i == -1:
            i = len(data)
        value = data[startfrom:i]
        return i + len(delim), value.decode()

def _params_parser(arr):
    ret = {}
    for i in arr:
        key,val = i.split('=')
        key = key.strip()
        val = val.strip()
        ret[key] = val
    return ret

class _headerDict(dict):
    def __getitem__(self, __key):
        return super().__getitem__(__key.lower())
    def __setitem__(self, __key, __value):
        super().__setitem__(__key.lower(), __value)
    def __contains__(self, __o):
        return super().__contains__(__o.lower())
    def __delitem__(self, __key):
        super().__delitem__(__key.lower())

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
        i, content_disposition = __getASCIIToDelim(data, b'\r\n', i)
        params = re.findall(r'form-data(?=.*(name)=([^;$]+))(?=.*(filename\*?)=([^;$]+))?.+', content_disposition)
        print (params)
        i += 4
'''

_media_types = {
    'application/x-www-form-urlencoded': {'property': 'form', 'parser': _application_x_www_form_urlencoded},
    'application/json': {'property':'json', 'parser': lambda data, charset: json.loads(data.decode(charset.lower()))}
}

class http_request:
    def __init__(self, request_data):
        self.__query_str = {}
        self.__json = {}
        self.__form = {}
        self.__obj = {}

        i, self.__method = __getASCIIToDelim(request_data, b' ')
        i, uri = __getASCIIToDelim(request_data, b' ', i)
        i, self.__version = __getASCIIToDelim(request_data, b'\r\n', i)
        
        headerEnd = request_data.find(b'\r\n\r\n')
        self.__headers = _headerDict()
        while i < headerEnd:
            if request_data[i] in [b' ', b'\t']:
                i, value = __getASCIIToDelim(request_data, b'\r\n', i)
                self.__headers[key] += ', ' + value.strip()
            else:
                i, key = __getASCIIToDelim(request_data, b': ', i)
                i, value = __getASCIIToDelim(request_data, b'\r\n', i)
                if key in self.__headers:
                    self.__headers[key] += ', ' + value
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

    @staticmethod
    def extend_supported_content_types(mimetype, parser_function, inst_property = 'obj'):
        if not callable(parser_function):
            raise Exception('parser_function must be a callable function')
        _media_types[mimetype] = {'parser': parser_function, 'property': inst_property if inst_property in ['obj', 'json', 'form'] else 'obj'}
    
    def parseData(self):
        if not self.__data:
            return
        if 'content-type' not in self.__headers:
            self.__headers['content-type'] = 'application/x-www-form-urlencoded'
        content_type = self.__headers['content-type'].split(';')
        content_type_params = _params_parser(content_type[1:])
        if 'charset' not in content_type_params:
            content_type_params['charset'] = 'utf-8'
        if content_type[0] in _media_types:
            func = self.__obj = _media_types[content_type[0]]['parser']
            self.__obj = _media_types[content_type[0]]['parser'](self.__data, **{k:v for k,v in content_type_params.items() if k in signature(func).parameters})
            if 'property' in _media_types[content_type[0]] and _media_types[content_type[0]]['property'] != 'obj':
                self.__setattr__(f'_{self.__class__.__name__}__{_media_types[content_type[0]]["property"]}', self.__obj)
    
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
