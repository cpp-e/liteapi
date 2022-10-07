from inspect import signature

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
        return self.methodFunc(*args, **kwargs, **{k:v for k,v in authParams.items() if k in signature(self.methodFunc).parameters})

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
