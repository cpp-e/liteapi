from .errno import *
class APIException(Exception):
    def __init__(self, code, *args):
        self.code = code
        self.strerror = strerror(code)
        super().__init__(*args)

APIError = APIException

# Client Errors Exceptions
UNAUTHORIZED_ERROR = lambda *args: APIException(UNAUTHORIZED, *args)
PAYMENT_REQUIRED_ERROR = lambda *args: APIException(PAYMENT_REQUIRED, *args)
NOT_FOUND_ERROR = lambda *args: APIException(NOT_FOUND, *args)
METHOD_NOT_ALLOWED_ERROR = lambda *args: APIException(METHOD_NOT_ALLOWED, *args)
REQUEST_TIMEOUT_ERROR = lambda *args: APIException(REQUEST_TIMEOUT, *args)
UNSUPPORTED_MEDIA_TYPE_ERROR = lambda *args: APIException(UNSUPPORTED_MEDIA_TYPE, *args)
TOO_MANY_REQUESTS_ERROR = lambda *args: APIException(TOO_MANY_REQUESTS, *args)
UNAVAILABLE_FOR_LEGAL_REASONS_ERROR = lambda *args: APIException(UNAVAILABLE_FOR_LEGAL_REASONS, *args)

# Server Errors Exceptions
INTERNAL_SERVER_ERROR_ERROR = lambda *args: APIException(INTERNAL_SERVER_ERROR, *args)
NOT_IMPLEMENTED_ERROR = lambda *args: APIException(NOT_IMPLEMENTED, *args)
HTTP_VERSION_NOT_SUPPORTED_ERROR = lambda *args: APIException(HTTP_VERSION_NOT_SUPPORTED, *args)
INSUFFICIENT_STORAGE_ERROR = lambda *args: APIException(INSUFFICIENT_STORAGE, *args)