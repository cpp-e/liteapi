class BaseAPIRequest:
    __definition = None
    __request = None
    __response = None
    __methods = None
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
            header = '{}{}: {}\r\n'.format(header, key, self.__response[key])
        return header

    @property
    def methods(self):
        return self.__methods
    
    @property
    def vars(self):
        return self.__uriVars
    
    def __getitem__(self, k):
        return self.__request[k]
