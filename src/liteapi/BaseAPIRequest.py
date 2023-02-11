from inspect import signature
from .verifiers.exception import *
from .APIModel import APIModel
from re import search, sub

class APIAuth:
    '''
    Used as an annotation to hint the framework that the function requires the authenticated data
    '''

class APIMethod:
    responses = None
    defaultResponse = False
    description = None
    methodFunc = None
    authenticator = None
    args = None
    returnType = None

    @staticmethod
    def create(methodFunc, authFunc = None, description = None):
        if isinstance(methodFunc, APIMethod):
            if authFunc and not methodFunc.authenticator:
                methodFunc.authenticator = authFunc
            if description and not methodFunc.description:
                methodFunc.description = description
            return methodFunc
        if callable(methodFunc):
            return APIMethod(methodFunc=methodFunc, authFunc=authFunc, description=description)
        raise Exception('Unsupported method type')

    def __init__(self, methodFunc, authFunc = None, description = None):
        self.methodFunc = methodFunc
        self.authenticator = authFunc
        self.args = {}
        self.__doc__ = methodFunc.__doc__
        self.description = description
        self.responses = []
        if self.__doc__:
            m = search(r'/breif:([^$\r\n]+)', methodFunc.__doc__)
            if m:
                self.description = m.group(1).strip()
                self.__doc__ = self.__doc__.replace(m.group(0),"")
            self.__doc__ = sub('[\r\n]', '', self.__doc__).strip()

        for a in self.methodFunc.__annotations__:
            if self.methodFunc.__annotations__[a] is not APIAuth:
                if a == 'return':
                    self.returnType = self.methodFunc.__annotations__[a]
                else:
                    self.args[a] = self.methodFunc.__annotations__[a]
    
    def __call__(self, *args, **kwargs):
        authParams = {}
        if self.authenticator:
            authParams = self.authenticator(*args, **kwargs)
        nkwargs = {}
        nkwargs.update(kwargs)
        methodArgs = signature(self.methodFunc).parameters
        for arg in methodArgs:
            if arg in kwargs:
                if methodArgs[arg].annotation in (str, int, float):
                    nkwargs[arg] = methodArgs[arg].annotation(nkwargs[arg])
            elif methodArgs[arg].annotation is APIAuth:
                authData = APIAuth()
                authData.__dict__.update(authParams)
                nkwargs[arg] = authData
            elif issubclass(methodArgs[arg].annotation, APIModel) or methodArgs[arg].annotation in (list, tuple):
                try:
                    nkwargs[arg] = methodArgs[arg].annotation(args[0].request.obj)
                except Exception as e:
                    print(str(e))
                    raise BAD_REQUEST_ERROR(error="Invalid Data", error_description=str(e))
        returned = self.methodFunc(*args, **nkwargs)
        returnCode = None
        if isinstance(returned, tuple) and len(returned) == 2 \
           and isinstance(returned[0], int) and returned[0] >= 100 and returned[0] < 600:
            returnCode, returned = returned
        if not self.defaultResponse and self.responses:
            for r in self.responses:
                if len(r) == 3:
                    if isinstance(returned, r[2]) and (not returnCode or returnCode == r[0]):
                        return r[0], returned
                else:
                    return r[0], returned
            raise Exception(f'Invalid {self.methodFunc.__name__} response')
        elif self.returnType:
            return self.returnType(returned) if not returnCode else (returnCode, self.returnType(returned))
        return returned if not returnCode else (returnCode, returned)

class BaseAPIRequest:
    __definition = None
    __regex = None
    __request = None
    __response = None
    __methods = None
    __methods_keys = None
    __uriVars = None
    _hasDoc = True
    app = None
    section = "default"

    @property
    def definition(self):
        return self.__definition
    
    @property
    def regex(self):
        return self.__regex

    @property
    def request(self):
        return self.__request

    @property
    def response(self):
        return self.__response

    @property
    def responseHeader(self):
        header = ""
        for key in self.__response:
            if isinstance(self.__response[key], str):
                header += '{}: {}\r\n'.format(key, self.__response[key])
            else:
                for val in self.__response[key]:
                    header += '{}: {}\r\n'.format(key, val)
        return header

    @property
    def methods(self):
        return self.__methods

    @property
    def methods_keys(self):
        return self.__methods_keys

    @property
    def vars(self):
        return self.__uriVars

    def __getitem__(self, k):
        return self.__request[k]

def addResponse(responseCode:int, responseMessage:str, returnCls = None):
    def inner(requestMethod):
        method = APIMethod.create(methodFunc=requestMethod)
        if isinstance(responseCode, int) and isinstance(responseMessage, str):
            if isinstance(returnCls, type) and issubclass(returnCls, APIModel):
                method.responses.append((responseCode, responseMessage, returnCls))
            else:
                method.responses.append((responseCode, responseMessage))
        else:
            raise Exception('responseCode must be an integer and responseMessage must be a string')
        return method
    return inner