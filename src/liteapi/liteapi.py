import re, socket, errno
from threading import Thread
from signal import signal, SIGINT, SIGTERM
from datetime import datetime
from time import time
from .BaseAPIRequest import BaseAPIRequest, APIMethod
from .http_request import http_request
from .http_response import http_response
from .error_no import *
from .exception import *
from .docs.docs import _docs
from ._internals import _iuList, _parse_unicode_value
from . import LITEAPI_SUPPORTED_REQUEST_METHODS

class liteapi:
    class __version:
        MAJOR = 0
        MINOR = 5
        PATCH = 2
        
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
        self.__fixedHeaders = _iuList()
        self.__init_socket()
        self.__docs = _docs(self) if 'nodoc' not in kwargs or not kwargs['nodoc'] else None
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
        if(self.__docs):
            self.__docs.build()
        print("""API Server started on URL:
        http{}://{}:{}""".format('s' if self.__ssl else '', self.__config['host'], self.__config['port']))
        while self.__running:
            try:
                conn, addr = self.__socket.accept()
                thread = Thread(target=self.__handle_client, args=[conn, addr])
                thread.daemon = True
                thread.start()
            except:
                pass
    def register(self, uri, section='default'):
        def inner(requestClass):
            requestClass.section = section
            if not issubclass(requestClass, BaseAPIRequest):
                raise RuntimeError('{} must be a subclass of BaseAPIRequest'.format((requestClass).__name__))
            hasQuery = uri.find('?')
            regex = uri[:hasQuery] if hasQuery > 0 else uri
            definition = re.sub('{([^:}]+):(str|int|float|path)}', r'{\1}', regex)
            requestClass._BaseAPIRequest__definition = definition
            if not requestClass._BaseAPIRequest__methods:
                requestClass._BaseAPIRequest__methods = {}
            if not requestClass._BaseAPIRequest__methods_keys:
                requestClass._BaseAPIRequest__methods_keys = []
            requestClass._BaseAPIRequest__uriVars = {}

            ms = re.findall('\{(([^:}]+)(:(str|int|float|path))?)\}', regex)
            for m in ms:
                if len(m) > 3 and m[3] in ('int', 'float', 'path'):
                    if m[3] == 'int':
                        regex = regex.replace('{{{}}}'.format(m[0]), '([0-9]+)')
                        if m[1] not in requestClass._BaseAPIRequest__uriVars:
                            requestClass._BaseAPIRequest__uriVars[m[1]] = int
                    elif m[3] == 'float':
                        regex = regex.replace('{{{}}}'.format(m[0]), r'([0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+)')
                        if m[1] not in requestClass._BaseAPIRequest__uriVars:
                            requestClass._BaseAPIRequest__uriVars[m[1]] = float
                    elif m[3] == 'path':
                        regex = regex.replace(f'{{{m[0]}}}', '([^?&]+)')
                        if m[1] not in requestClass._BaseAPIRequest__uriVars:
                            requestClass._BaseAPIRequest__uriVars[m[1]] = str
                else:
                    regex = regex.replace('{{{}}}'.format(m[0]), '([^/?&]+?)')
                    if m[1] not in requestClass._BaseAPIRequest__uriVars:
                        requestClass._BaseAPIRequest__uriVars[m[1]] = str
                regex = regex.replace('{{{}}}'.format(m[0]), '([0-9]+)' if m[3] == 'int' else '([^/?&]+?)')
            requestClass._BaseAPIRequest__regex = regex

            for methodnam in LITEAPI_SUPPORTED_REQUEST_METHODS:
                if methodnam.lower() in dir(requestClass):
                    requestClass._BaseAPIRequest__methods[methodnam] = method = APIMethod.create(methodFunc=getattr(requestClass, methodnam.lower()))
                    args = {}
                    for arg in requestClass._BaseAPIRequest__uriVars:
                        args[arg] = requestClass._BaseAPIRequest__uriVars[arg]
                    args.update(method.args)
                    method.args = args
                    if len(method.responses) == 0:
                        if isinstance(method.returnType, type) and issubclass(method.returnType, APIModel):
                            method.responses.append((200, "Successful Response", method.returnType))
                        else:
                            method.responses.append((200, "Successful Response"))
                        method.defaultResponse = True
                    setattr(requestClass, methodnam.lower(), method)
                    requestClass._BaseAPIRequest__methods_keys.append(methodnam)

            self.__request[definition] = requestClass
            if(requestClass._hasDoc):
                print(f'API {requestClass._BaseAPIRequest__definition} is registered')
        return inner
    def extend_supported_request_content_types(self, mimetype, parser_function, override = False, request_property = 'obj'):
        http_request.extend_supported_content_types(mimetype, parser_function, override, request_property)
    def extend_supported_response_content_types(self, mimetype, parser_function, override = False):
        http_response.extend_supported_content_types(mimetype, parser_function, override)
    def add_fixed_headers(self, name, *args):
        self.__fixedHeaders.append(name)
        for a in args:
            self.__fixedHeaders.append(a)
    def __handle_client(self, sock, addr):
        BUFF_SIZE = 4096
        request_data = b''
        response_format = 'HTTP/1.1 {}\r\nContent-Length: {}\r\n{}\r\n'
        stime = 0
        while True:
            try:
                if not stime:
                    stime =  time()
                part = sock.recv(BUFF_SIZE)
                request_data += part
                if len(part) < BUFF_SIZE:
                    break
            except socket.error as e:
                err = e.args[0]
                if err in (errno.EAGAIN, errno.EWOULDBLOCK):
                    stime =  time()
                    continue
        if not request_data:
            sock.close()
            return
        
        try:
            request = http_request(request_data)
        except Exception as e:
            sock.close()
            return
        
        try:
            if request.version != 'HTTP/1.1':
                raise APIException(HTTP_VERSION_NOT_SUPPORTED)
            if request.method not in (*self.__supportedMethods, 'HEAD', 'OPTIONS'):
                raise APIException(METHOD_NOT_ALLOWED)
            request._http_request__protocol = f'http{"s" if self.__ssl else ""}'
            request._http_request__host = self.__config['host']
            request._http_request__port = self.__config['port']
            found, definition, vars = False, None, {}
            for definition in self.__request:
                ms = re.fullmatch(self.__request[definition]._BaseAPIRequest__regex, request.base_uri)
                if ms:
                    found = True
                    if request.method not in self.__request[definition]._BaseAPIRequest__methods and (request.method != 'HEAD' or (request.method == 'HEAD' and 'GET' not in self.__request[definition]._BaseAPIRequest__methods)):
                        raise APIException(NOT_IMPLEMENTED)
                    else:
                        var_keys = [k for k in self.__request[definition]._BaseAPIRequest__uriVars.keys()]
                        for i in range(len(self.__request[definition]._BaseAPIRequest__uriVars)):
                            vars[var_keys[i]] = _parse_unicode_value(self.__request[definition]._BaseAPIRequest__uriVars[var_keys[i]](ms[i + 1]))
                    break
            if not found:
                raise APIException(NOT_FOUND)
            
            request.parseData()

            copyRequest = self.__request[definition]()
            copyRequest.app = self
            copyRequest._BaseAPIRequest__request = request
            copyRequest._BaseAPIRequest__response = http_response()
            for f in self.__fixedHeaders:
                if f in request.headers:
                    copyRequest._BaseAPIRequest__response.headers[request.headers._lowerKeys[f.lower()]] = request.headers[f]
            copyRequest.client_address = addr[0]
            
            response_data = copyRequest.response.getResponse(copyRequest._BaseAPIRequest__methods[request.method if request.method != 'HEAD' else 'GET'](copyRequest, **vars))
            response_code = copyRequest.response.response_code
            response_status = RETURN_STATUS(response_code)
            response_header = copyRequest.response.responseHeader
            
        except APIException as e:
            response_code = e.code
            response_status = RETURN_STATUS(response_code)

            response = http_response()
            response.headers.update(e.header)
            response_data = response.getResponse(e.response if e.response else RETURN_STATUS_OBJ(response_code))
            response_header = response.responseHeader
        except Exception as e:
            response_code = INTERNAL_SERVER_ERROR
            response_status = RETURN_STATUS(INTERNAL_SERVER_ERROR)
            
            response = http_response()
            response_data = response.getResponse(RETURN_STATUS_OBJ(response_code))
            response_header = response.responseHeader
            print(e)
        
        response_bytes = response_format.format(response_status, len(response_data), response_header).encode()
        if(request.method != 'HEAD'):
            response_bytes += response_data
        sock.sendall(response_bytes)
        response_time = round(time() - stime, 5)
        print("{} - Request from {}: {} {} {}, {}{}\033[0m, {}s".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), addr[0], request.method, request.uri, request.version, '\033[92m' if response_code >= 200 and response_code < 300 else '\033[91m' if response_code >=400 else '',RETURN_STATUS(response_code), response_time))
        sock.shutdown(socket.SHUT_WR)
        sock.close()
    def __handle_signal(self, signum, frame):
        if signum == SIGINT:
            print('Received Ctrl+C signal')
            self.__running = False
        if signum == SIGTERM:
            print('Process Killed')
            self.__running = False
    def __init_socket(self):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.settimeout(1)
        server.bind((self.__config['host'], self.__config['port']))
        server.listen(5)
        signal(SIGINT, self.__handle_signal)
        signal(SIGTERM, self.__handle_signal)
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
        self.__socket.settimeout(1)
