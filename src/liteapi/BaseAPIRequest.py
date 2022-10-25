from inspect import signature
from .verifiers.exception import *
from .APIModel import APIModel

class APIAuth:
    '''
    Used as an annotation to hint the framework that the function requires the authenticated data
    '''

class APIMethod:
    description = None
    methodFunc = None
    authenticator = None

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
        self.description = description
    
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
            elif methodArgs[arg].annotation == APIAuth:
                authData = APIAuth()
                authData.__dict__.update(authParams)
                nkwargs[arg] = authData
            elif issubclass(methodArgs[arg].annotation, APIModel):
                try:
                    nkwargs[arg] = methodArgs[arg].annotation(args[0].request.obj)
                except Exception as e:
                    print(str(e))
                    raise BAD_REQUEST_ERROR(error="Invalid Data", error_description=str(e))

        return self.methodFunc(*args, **nkwargs)

class BaseAPIRequest:
    __definition = None
    __request = None
    __response = None
    __methods = None
    __methods_keys = None
    __uriVars = None

    @property
    def definition(self):
        return self.__definition

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
