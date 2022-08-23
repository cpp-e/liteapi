import re, socket, ssl, threading, signal, json, copy
from time import sleep
from datetime import datetime
from .BaseAPIRequest import BaseAPIRequest
from .http_request import http_request

class liteapi:
    class __version:
        MAJOR = 0
        MINOR = 1
        
        def __str__(self):
            return str("{}.{}".format(self.MAJOR, self.MINOR))
    
    @staticmethod
    def version():
        return liteapi.__version()
    
    __supportedMethods = ['DELETE', 'GET', 'POST', 'PUT']
    __defaultConfig = {
        'host': '127.0.0.1',
        'port': 8000
    }
    __response_codes = {
        '200': {'code': 200, 'message':'OK'},
        '404': {'code': 404, 'message':'Not Found'},
        '501': {'code': 501, 'message':'Not Implemented'}
    }
    def __init__(self, config = {}):
        self.__request = {}
        self.__verifyType(config, dict, "invalid config with {} type, expecting dict type".format(type(config).__name__))
        self.__config = liteapi.__defaultConfig.copy()
        self.__config.update(config)
        self.__init_socket()
        @self.register('/info')
        class infoClass (BaseAPIRequest):
            def get(myself):
                info = []
                for regex in [x for x in self._liteapi__request if x != '/info']:
                    info.append({'uri': self._liteapi__request[regex].definition, 'methods': self._liteapi__request[regex].methods})
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
        http{}://{}:{}""".format('s' if 'ssl' in self.__config else '', self.__config['host'], self.__config['port']))
        while self.__running:
            try:
                conn, addr = self.__socket.accept()
                thread = threading.Thread(target=self.__handle_client, args=[conn])
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
            request = requestClass(re.sub(':(str|int)', '', regex))
            ms = re.findall('\{(([^:}]+)(:(str|int))?)\}', regex)
            for m in ms:
                if len(m) > 3 and m[3] == 'int':
                    regex = regex.replace('{{{}}}'.format(m[0]), '([0-9]+)')
                    request.addVariable(m[1], int)
                else:
                    regex = regex.replace('{{{}}}'.format(m[0]), '([^/?&]+?)')
                    request.addVariable(m[1], str)
                regex = regex.replace('{{{}}}'.format(m[0]), '([0-9]+)' if m[3] == 'int' else '([^/?&]+?)')
            self.__request[regex] = request
        return inner
    def __handle_client(self, sock):
        BUFF_SIZE = 4096
        request_data = b''
        response = 'HTTP/1.1 {} {}\r\ncontent-length: {}\r\ncontent-type: {}\r\n\r\n{}'
        while True:
            try:
                part = sock.recv(BUFF_SIZE)
                request_data += part
                if len(part) < BUFF_SIZE:
                    break
            except socket.error as e:
                err = e.args[0]
                if err in (socket.EAGAIN, socket.EWOULDBLOCK):
                    sleep(0.1)
                    continue
            else:
                pass
        request = http_request(request_data)

        if request.method in self.__supportedMethods:
            response_code = liteapi.__response_codes['404']
            uriRegex = None
            vars = {}
            for uriRegex in self.__request:
                ms = re.fullmatch(uriRegex, request.uri)
                if ms:
                    if not request.method in self.__request[uriRegex].methods:
                        response_code = liteapi.__response_codes['501']
                    else:
                        response_code = liteapi.__response_codes['200']
                        for i in range(len(self.__request[uriRegex].variables)):
                            variable = self.__request[uriRegex].variables[i]
                            vars[variable] = self.__request[uriRegex].varType[variable](ms[i + 1])
                    break
            copyRequest = copy.deepcopy(self.__request[uriRegex])
            copyRequest._setRequest(request)
            response_data = json.dumps({'status':  response_code, 'data': copyRequest[request.method](**vars) if response_code['code'] == 200 else 'Invalid Request'})
            print("{} - Request from {}: {} {} {}, {}{} {}\033[0m".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sock.getpeername()[0], request.method, request.uri, request.version, '\033[92m' if response_code['code'] == 200 else '\033[91m',response_code['code'], response_code['message']))
            sock.sendall(response.format(response_code['code'], response_code['message'], len(response_data), 'application/json; charset=utf-8', response_data).encode())
        sock.shutdown(socket.SHUT_WR)
        sock.close()
    def __handle_signal(self, signum, frame):
        if signum == signal.SIGINT:
            print('Received Ctrl+C signal')
            self.__running = False
        if signum == signal.SIGTERM:
            print('Process Killed')
            self.__running = False
    def __verifyType(self, object, etype, message = ''):
        if type(object) != etype:
            raise TypeError(message)
    def __init_socket(self):
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(False)
        server.bind((self.__config['host'], self.__config['port']))
        server.listen(5)
        signal.signal(signal.SIGINT, self.__handle_signal)
        signal.signal(signal.SIGTERM, self.__handle_signal)
        if 'ssl' in self.__config:
            if not 'certfile' in self.__config['ssl']:
                raise ssl.SSLError("Missing certfile under ssl configuration")
            if not 'keyfile' in self.__config['ssl']:
                raise ssl.SSLError("Missing keyfile under ssl configuration")
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.__config['ssl']['certfile'], self.__config['ssl']['keyfile'], self.__config['ssl']['keypassword'] if 'keypassword' in self.__config['ssl'] else None)
            self.__socket = context.wrap_socket(server, server_side=True)
        else:
            self.__socket = server
