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

class http_request:
    def __init__(self, request_data):
        self.__query_str = {}
        self.__json = {}
        self.__form = {}

        i, self.__method = self.__getASCIIToDelim(request_data, b' ')
        i, uri = self.__getASCIIToDelim(request_data, b' ', i)
        i, self.__version = self.__getASCIIToDelim(request_data, b'\r\n', i)
        
        headerEnd = request_data.find(b'\r\n\r\n')
        self.__headers = {}
        while i < headerEnd:
            if request_data[i] in [b' ', b'\t']:
                i, value = self.__getASCIIToDelim(request_data, b'\r\n', i)
                self.__headers[key] += ', ' + value.strip()
            else:
                i, key = self.__getASCIIToDelim(request_data, b': ', i)
                i, value = self.__getASCIIToDelim(request_data, b'\r\n', i)
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
        
    def __getASCIIToDelim(self, data, delim, startfrom = 0):
        i = data.find(delim, startfrom)
        if i == -1:
            i = len(data)
        value = data[startfrom:i]
        return i + len(delim), value.decode()
    
    def parseData(self):
        if 'Content-Type' not in self.__headers or 'x-www-form-urlencoded' in self.__headers['Content-Type']:
            fs = self.__data.decode().split('&')
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
                    if var not in self.__form:
                        self.__form[var] = []
                    self.__form[var].append(val)
                else:
                    self.__form[var] = val
        else:
            if 'json' in self.__headers['Content-Type']:
                if self.__data:
                    self.__json = json.loads(self.__data.decode())
            #elif 'form-data' in self.__headers['Content-Type']:
            #    boundary = '--' + re.findall('boundary="?([^;$"]+)"?', self.__headers['Content-Type'])[0] + '\r\n'
            #    i = 0
            #    while i < len(self.__data):
            #        t = self.__data[i:len(boundary)].decode()
            #        if self.__data[i:len(boundary)].decode() == boundary:
            #            i += len(boundary)
            #            i, content_disposition = self.__getASCIIToDelim(self.__data, b'\r\n', i)
            #            params = re.findall(r'form-data(?=.*(name)=([^;$]+))(?=.*(filename\*?)=([^;$]+))?.+', content_disposition)
            #            print (params)
            #            i += 4
    
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
    def form(self):
        return self.__form

    @property
    def query_string(self):
        return self.__query_str
