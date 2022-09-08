from .errno import *
class APIException(Exception):
    def __init__(self, code, *args, **kwargs):
        self.code = code
        self.strerror = strerror(code)
        self.response = kwargs
        self.__header = {'content-type': 'application/json; charset=utf-8'}
        if args:
            i = 0
            if isinstance(args[i], str):
                self.strerror = args[i]
                i += 1
            while i < len(args) and isinstance(args[i], dict):
                self.__header.update(args[i])
                i += 1
        super().__init__(*args)
    
    @property
    def responseHeader(self):
        header = ""
        for key in self.__header:
            header = '{}{}: {}\r\n'.format(header, key, self.__header[key])
        return header


APIError = APIException

# Client Errors Exceptions
BAD_REQUEST_ERROR = lambda *args, **kwargs: APIException(BAD_REQUEST, *args, **kwargs)
UNAUTHORIZED_ERROR = lambda *args, **kwargs: APIException(UNAUTHORIZED, *args, **kwargs)
PAYMENT_REQUIRED_ERROR = lambda *args, **kwargs: APIException(PAYMENT_REQUIRED, *args, **kwargs)
FORBIDDEN_ERROR = lambda *args, **kwargs: APIException(FORBIDDEN, *args, **kwargs)
NOT_FOUND_ERROR = lambda *args, **kwargs: APIException(NOT_FOUND, *args, **kwargs)
METHOD_NOT_ALLOWED_ERROR = lambda *args, **kwargs: APIException(METHOD_NOT_ALLOWED, *args, **kwargs)
REQUEST_TIMEOUT_ERROR = lambda *args, **kwargs: APIException(REQUEST_TIMEOUT, *args, **kwargs)
UNSUPPORTED_MEDIA_TYPE_ERROR = lambda *args, **kwargs: APIException(UNSUPPORTED_MEDIA_TYPE, *args, **kwargs)
TOO_MANY_REQUESTS_ERROR = lambda *args, **kwargs: APIException(TOO_MANY_REQUESTS, *args, **kwargs)
UNAVAILABLE_FOR_LEGAL_REASONS_ERROR = lambda *args, **kwargs: APIException(UNAVAILABLE_FOR_LEGAL_REASONS, *args, **kwargs)

# Server Errors Exceptions
INTERNAL_SERVER_ERROR_ERROR = lambda *args, **kwargs: APIException(INTERNAL_SERVER_ERROR, *args, **kwargs)
NOT_IMPLEMENTED_ERROR = lambda *args, **kwargs: APIException(NOT_IMPLEMENTED, *args, **kwargs)
HTTP_VERSION_NOT_SUPPORTED_ERROR = lambda *args, **kwargs: APIException(HTTP_VERSION_NOT_SUPPORTED, *args, **kwargs)
INSUFFICIENT_STORAGE_ERROR = lambda *args, **kwargs: APIException(INSUFFICIENT_STORAGE, *args, **kwargs)