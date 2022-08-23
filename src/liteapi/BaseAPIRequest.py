class BaseAPIRequest:
    def __init__(self, definition):
        self.__definition = definition
        self.__request = None
        self.__methods = {}
        self.__uriVars = {}
        if 'delete' in dir(self):
            self.__methods['DELETE'] = self.delete
        if 'get' in dir(self):
            self.__methods['GET'] = self.get
        if 'post' in dir(self):
            self.__methods['POST'] = self.post
        if 'put' in dir(self):
            self.__methods['PUT'] = self.put
    
    def _setRequest(self, request):
        self.__request = request
    
    def addVariable(self, varName, type):
        if varName in self.__uriVars:
            return False
        self.__uriVars[varName] = type
        return True

    @property
    def varType(self):
        return self.__uriVars
    
    @property
    def definition(self):
        return self.__definition

    @property
    def methods(self):
        keys = []
        for key in self.__methods.keys():
            keys.append(key)
        return keys
    
    @property
    def variables(self):
        keys = []
        for key in self.__uriVars.keys():
            keys.append(key)
        return keys
    
    @property
    def request(self):
        return self.__request
    
    def __getitem__(self, key):
        return self.__methods[key]
