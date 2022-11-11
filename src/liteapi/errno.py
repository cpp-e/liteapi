# Information Responses
CONTINUE = 100
SWITCHING_PROTOCOLS = 101
PROCESSING = 102
EARLY_HINTS = 103

# Successful Responses
RESPONSE_OK = 200
CREATED = 201
ACCEPTED = 202
NON_AUTHORITATIVE_INFORMATION = 203
NO_CONTENT = 204
RESET_CONTENT = 205
PARTIAL_CONTENT = 206
MULTI_STATUS = 207
ALREADY_REPORTED = 208
IM_USED = 209

# Redirection Messages
MULTIPLE_CHOICES = 300
MOVED_PERMANENTLY = 301
FOUND = 302
SEE_OTHER = 303
NOT_MODIFIED = 304
USE_PROXY = 305
TEMPORARY_REDIRECT = 307
PERMANENT_REDIRECT = 308

# Client Errors
BAD_REQUEST = 400
UNAUTHORIZED = 401
PAYMENT_REQUIRED = 402
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
NOT_ACCEPTED = 406
PROXY_AUTHENTICATION_REQUIRED = 407
REQUEST_TIMEOUT = 408
CONFLICT = 409
GONE = 410
LENGTH_REQUIRED = 411
PRECONDITION_FAILED = 412
PAYLOAD_TOO_LARGE = 413
URI_TOO_LONG = 414
UNSUPPORTED_MEDIA_TYPE = 415
RANGE_NOT_SATISFIABLE = 416
EXPECTATION_FAILED = 417
IM_A_TEAPOT = 418
MISDIRECTED_REQUEST = 421
UNPROCESSABLE_ENTITY = 422
LOCKED = 423
FAILED_DEPENDENCY = 424
TOO_EARLY = 425
UPGRADE_REQUIRED = 426
PRECONDITION_REQUIRED = 428
TOO_MANY_REQUESTS = 429
REQUEST_HEADER_FIELDS_TOO_LARGE = 431
UNAVAILABLE_FOR_LEGAL_REASONS = 451

# Server Errors
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503
GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 505
VARIANT_ALSO_NEGOTIATES = 506
INSUFFICIENT_STORAGE = 507
LOOP_DETECTED = 508
NOT_EXTENDED = 510
NETWORK_AUTHENTICATION_REQUIRED = 511

_strerror = {
    CONTINUE: 'Continue',
    SWITCHING_PROTOCOLS: 'Switching Protocols',
    PROCESSING: 'Processing',
    EARLY_HINTS: 'Early Hints',
    RESPONSE_OK: 'OK',
    CREATED: 'Created',
    ACCEPTED: 'Accepted',
    NON_AUTHORITATIVE_INFORMATION: 'Non-Authoritative Information',
    NO_CONTENT: 'No Content',
    RESET_CONTENT: 'Reset Content',
    PARTIAL_CONTENT: 'Partial Content',
    MULTI_STATUS: 'Multi-Status',
    ALREADY_REPORTED: 'Already Reported',
    IM_USED: 'IM Used',
    MULTIPLE_CHOICES: 'Multiple Choices',
    MOVED_PERMANENTLY: 'Moved Permanently',
    FOUND: 'Found',
    SEE_OTHER: 'See Other',
    NOT_MODIFIED: 'Not Modified',
    USE_PROXY: 'Use Proxy',
    TEMPORARY_REDIRECT: 'Temporary Redirection',
    PERMANENT_REDIRECT: 'Permanent Redirection',
    BAD_REQUEST: 'Bad Request',
    UNAUTHORIZED: 'Unauthorized',
    PAYMENT_REQUIRED: 'Payment Required',
    FORBIDDEN: 'Forbidden',
    NOT_FOUND: 'Not Found',
    METHOD_NOT_ALLOWED: 'Method Not Allowed',
    NOT_ACCEPTED: 'Not Accepted',
    PROXY_AUTHENTICATION_REQUIRED: 'Proxy Authentication Required',
    REQUEST_TIMEOUT: 'Request Timeout',
    CONFLICT: 'Conflict',
    GONE: 'Gone',
    LENGTH_REQUIRED: 'Length Required',
    PRECONDITION_FAILED: 'Precondition Failed',
    PAYLOAD_TOO_LARGE: 'Payload Too Large',
    URI_TOO_LONG: 'URI Too Long',
    UNSUPPORTED_MEDIA_TYPE: 'Unsupported Media Type',
    RANGE_NOT_SATISFIABLE: 'Range Not Satisfiable',
    EXPECTATION_FAILED: 'Expectation Failed',
    IM_A_TEAPOT: 'I\'m A Teapot',
    MISDIRECTED_REQUEST: 'Misdirected Request',
    UNPROCESSABLE_ENTITY: 'Unprocessable Entity',
    LOCKED: 'Locked',
    FAILED_DEPENDENCY: 'Failed Dependency',
    TOO_EARLY: 'Too Early',
    UPGRADE_REQUIRED: 'Upgrade Required',
    PRECONDITION_REQUIRED: 'Precondition Required',
    TOO_MANY_REQUESTS: 'Too Many Requests',
    REQUEST_HEADER_FIELDS_TOO_LARGE: 'Request Header Fields Too Large',
    UNAVAILABLE_FOR_LEGAL_REASONS: 'Unavailable For Legal Reasons',
    INTERNAL_SERVER_ERROR: 'Internal Server Error',
    NOT_IMPLEMENTED: 'Not Implemented',
    BAD_GATEWAY: 'Bad Gateway',
    SERVICE_UNAVAILABLE: 'Service Unavailable',
    GATEWAY_TIMEOUT: 'Gateway Timeout',
    HTTP_VERSION_NOT_SUPPORTED: 'HTTP Version Not Supported',
    VARIANT_ALSO_NEGOTIATES: 'Variant Also Negotiates',
    INSUFFICIENT_STORAGE: 'Insuffecient Storage',
    LOOP_DETECTED: 'Loop Detected',
    NOT_EXTENDED: 'Not Extended',
    NETWORK_AUTHENTICATION_REQUIRED: 'Network Authentication Required'
}

strerror = lambda c : _strerror[c] if c in _strerror else 'Unknown Response'

from .APIModel import APIModel
from .docs.annotate import Annotate

class ResponseStatus(APIModel):
    code: Annotate(int, doc="Response Status Code", example=200)
    message: Annotate(str, doc="Response Status Message", example="OK")

RETURN_STATUS = lambda c : '{} {}'.format(c, strerror(c))
RETURN_STATUS_OBJ = lambda c : ResponseStatus({'code': c, 'message': strerror(c)})