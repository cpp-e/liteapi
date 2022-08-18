import re, json
class http_request:
    def __init__(self, request_data):
        self.__query_str = {}
        i, self.__method = self.__getASCIIToDelim(request_data, b' ')
        i, uri = self.__getASCIIToDelim(request_data, b' ', i)
        i, self.__version = self.__getASCIIToDelim(request_data, b'\r\n', i)
        
        headerEnd = request_data.find(b'\r\n\r\n')
        self.__headers = {}
        while i < headerEnd:
            i, key = self.__getASCIIToDelim(request_data, b': ', i)
            i, value = self.__getASCIIToDelim(request_data, b'\r\n', i)
            self.__headers[key] = value            
        self.__data = request_data[i+2:]

        hasQuery = uri.find('?')
        self.__uri = uri[:hasQuery] if hasQuery > 0 else uri

        if hasQuery > 0:
            qs = uri[hasQuery+1:].split('&')
            for q in qs:
                try:
                    var, val = q.split('=')
                    for m in re.findall('((%[0-9a-fA-F]{2})+)', val):
                        val = val.replace(m if m is str else m[0], bytearray.fromhex(m[1:] if m is str else m[0].replace('%', '')).decode('utf-8'), 1)
                except:
                    var, val = q, None
                for m in re.findall('((%[0-9a-fA-F]{2})+)', var):
                    var = var.replace(m if m is str else m[0], bytearray.fromhex(m[1:] if m is str else m[0].replace('%', '')).decode('utf-8'), 1)
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
        value = data[startfrom:i]
        return i + len(delim), value.decode()
    
    @property
    def method(self):
        return self.__method
    @property
    def uri(self):
        return self.__uri
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
        return json.loads(self.__data.decode())

    @property
    def query_string(self):
        return self.__query_str
