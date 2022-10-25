import re, socket, threading, signal, json, errno, time
from time import sleep
from datetime import datetime
from .BaseAPIRequest import BaseAPIRequest, APIMethod
from .APIModel import APIJSONEncoder, APIModel
from .http_request import http_request
from .errno import *
from .exception import *
from . import LITEAPI_SUPPORTED_REQUEST_METHODS

RETURN_STATUS = lambda c : '{} {}'.format(c, strerror(c))
RETURN_STATUS_OBJ = lambda c : {'code': c, 'message': strerror(c)}

JSON_UTF8 = 'application/json; charset=utf-8'

class liteapi:
    class __version:
        MAJOR = 0
        MINOR = 4
        PATCH = 1
        
        def __str__(self):
            return str("{}.{}.{}".format(self.MAJOR, self.MINOR, self.PATCH))
    
    @staticmethod
    def version():
        return liteapi.__version()
    
    __supportedMethods = LITEAPI_SUPPORTED_REQUEST_METHODS
    __defaultConfig = {
        'host': '127.0.0.1',
        'port': 8000
    }
    def __init__(self, **kwargs):
        self.__ssl = False
        self.__request = {}
        self.__config = liteapi.__defaultConfig.copy()
        self.__config.update(kwargs)
        self.__init_socket()
        @self.register('/info')
        class infoClass (BaseAPIRequest):
            def get(myself):
                info = []
                for regex in self._liteapi__request:
                    info.append({'uri': self._liteapi__request[regex]._BaseAPIRequest__definition, 'methods': self._liteapi__request[regex]._BaseAPIRequest__methods_keys})
                return info
    def __del__(self):
        self.close()
    def close(self):
        print("Closing API server")
        self.__running = False
        if '_liteapi__socket' in dir(self):
            try:
                self.__socket.shutdown(socket.SHUT_RDWR)
                self.__socket.close()
            except:
                pass
            self.__socket = None
    def run(self):
        self.__running = True
        print("""API Server started on URL:
        http{}://{}:{}""".format('s' if self.__ssl else '', self.__config['host'], self.__config['port']))
        while self.__running:
            try:
                conn, addr = self.__socket.accept()
                thread = threading.Thread(target=self.__handle_client, args=[conn, addr])
                thread.daemon = True
                thread.start()
            except:
                pass
    def register(self, uri):
        def inner(requestClass):
            if not issubclass(requestClass, BaseAPIRequest):
                raise RuntimeError('{} must be a subclass of BaseAPIRequest'.format((requestClass).__name__))
            hasQuery = uri.find('?')
            regex = uri[:hasQuery] if hasQuery > 0 else uri
            requestClass._BaseAPIRequest__definition = re.sub(':(str|int|float)', '', regex)
            if not requestClass._BaseAPIRequest__methods:
                requestClass._BaseAPIRequest__methods = {}
            if not requestClass._BaseAPIRequest__methods_keys:
                requestClass._BaseAPIRequest__methods_keys = []
            requestClass._BaseAPIRequest__response = {'content-type': JSON_UTF8}
            requestClass._BaseAPIRequest__uriVars = {}

            for methodnam in LITEAPI_SUPPORTED_REQUEST_METHODS:
                if methodnam.lower() in dir(requestClass):
                    requestClass._BaseAPIRequest__methods[methodnam] = method = APIMethod.create(methodFunc=getattr(requestClass, methodnam.lower()))
                    setattr(requestClass, methodnam.lower(), method)
                    requestClass._BaseAPIRequest__methods_keys.append(methodnam)
            
            ms = re.findall('\{(([^:}]+)(:(str|int|float))?)\}', regex)
            for m in ms:
                if len(m) > 3 and m[3] in ['int', 'float']:
                    if m[3] == 'int':
                        regex = regex.replace('{{{}}}'.format(m[0]), '([0-9]+)')
                        if m[1] not in requestClass._BaseAPIRequest__uriVars:
                            requestClass._BaseAPIRequest__uriVars[m[1]] = int
                    elif m[3] == 'float':
                        regex = regex.replace('{{{}}}'.format(m[0]), r'([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)')
                        if m[1] not in requestClass._BaseAPIRequest__uriVars:
                            requestClass._BaseAPIRequest__uriVars[m[1]] = float
                else:
                    regex = regex.replace('{{{}}}'.format(m[0]), '([^/?&]+?)')
                    if m[1] not in requestClass._BaseAPIRequest__uriVars:
                        requestClass._BaseAPIRequest__uriVars[m[1]] = str
                regex = regex.replace('{{{}}}'.format(m[0]), '([0-9]+)' if m[3] == 'int' else '([^/?&]+?)')
            self.__request[regex] = requestClass
        return inner
    def extend_supported_content_types(self, mimetype, parser_function, request_property = 'obj'):
        http_request.extend_supported_content_types(mimetype, parser_function, request_property)
    def __handle_client(self, sock, addr):
        BUFF_SIZE = 4096
        request_data = b''
        response = 'HTTP/1.1 {}\r\ncontent-length: {}\r\n{}\r\n{}'
        stime = 0
        while True:
            try:
                if not stime:
                    stime =  time.time()
                part = sock.recv(BUFF_SIZE)
                request_data += part
                if len(part) < BUFF_SIZE:
                    break
            except socket.error as e:
                err = e.args[0]
                if err in (errno.EAGAIN, errno.EWOULDBLOCK):
                    stime =  time.time()
                    continue
        if not request_data:
            sock.close()
            return
        request = http_request(request_data)
        try:
            if request.version != 'HTTP/1.1':
                raise APIException(HTTP_VERSION_NOT_SUPPORTED)
            if request.method not in self.__supportedMethods:
                raise APIException(METHOD_NOT_ALLOWED)
            found, uriRegex, vars = False, None, {}
            for uriRegex in self.__request:
                ms = re.fullmatch(uriRegex, request.base_uri)
                if ms:
                    found = True
                    if request.method not in self.__request[uriRegex]._BaseAPIRequest__methods and (request.method != 'HEAD' or (request.method == 'HEAD' and 'GET' not in self.__request[uriRegex]._BaseAPIRequest__methods)):
                        raise APIException(NOT_IMPLEMENTED)
                    else:
                        for i in range(len(self.__request[uriRegex]._BaseAPIRequest__uriVars)):
                            variable = [k for k in self.__request[uriRegex]._BaseAPIRequest__uriVars.keys()][i]
                            vars[variable] = self.__request[uriRegex]._BaseAPIRequest__uriVars[variable](ms[i + 1])
                    break
            if not found:
                raise APIException(NOT_FOUND)
            
            response_code = RESPONSE_OK
            response_status = RETURN_STATUS(response_code)
            copyRequest = self.__request[uriRegex]()
            copyRequest._BaseAPIRequest__request = request
            copyRequest.client_address = addr[0]

            request.parseData()
            
            response_data_raw = copyRequest._BaseAPIRequest__methods[request.method if request.method != 'HEAD' else 'GET'](copyRequest, **vars)

            if('json' in copyRequest.response['content-type'] and isinstance(response_data_raw, (dict, list, tuple, APIModel))):
                response_data = json.dumps(response_data_raw, cls=APIJSONEncoder)
            else:
                response_data = response_data_raw
            response_header = copyRequest.responseHeader
            
        except APIException as e:
            response_code = e.code
            response_status = RETURN_STATUS(response_code)
            
            response_data = json.dumps(e.response if e.response else RETURN_STATUS_OBJ(response_code))
            response_header = e.responseHeader
        except Exception as e:
            response_code = INTERNAL_SERVER_ERROR
            response_status = RETURN_STATUS(INTERNAL_SERVER_ERROR)

            response_data = json.dumps(RETURN_STATUS_OBJ(response_code))
            response_header = 'content-type: {}\r\n'.format(JSON_UTF8)
            print(e)
        
        sock.sendall(response.format(response_status, len(response_data), response_header, response_data if request.method != 'HEAD' else '').encode())
        response_time = round(time.time() - stime, 5)
        print("{} - Request from {}: {} {} {}, {}{}\033[0m, {}s".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), addr[0], request.method, request.uri, request.version, '\033[92m' if response_code == RESPONSE_OK else '\033[91m',RETURN_STATUS(response_code), response_time))
        sock.shutdown(socket.SHUT_WR)
        sock.close()
    def __handle_signal(self, signum, frame):
        if signum == signal.SIGINT:
            print('Received Ctrl+C signal')
            self.__running = False
        if signum == signal.SIGTERM:
            print('Process Killed')
            self.__running = False
    def __init_socket(self):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(False)
        server.bind((self.__config['host'], self.__config['port']))
        server.listen(5)
        signal.signal(signal.SIGINT, self.__handle_signal)
        signal.signal(signal.SIGTERM, self.__handle_signal)
        if 'ssl_certfile' in self.__config or 'ssl_keyfile' in self.__config:
            import ssl
            if 'ssl_certfile' not in self.__config:
                raise ssl.SSLError("Missing ssl_certfile")
            elif 'ssl_keyfile' not in self.__config:
                raise ssl.SSLError("Missing ssl_keyfile")
            else:
                self.__ssl = True
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(self.__config['ssl_certfile'], self.__config['ssl_keyfile'], self.__config['ssl_keypassword'] if 'ssl_keypassword' in self.__config else None)
                self.__socket = context.wrap_socket(server, server_side=True)
        else:
            self.__socket = server
