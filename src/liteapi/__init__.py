LITEAPI_SUPPORTED_REQUEST_METHODS = ('DELETE', 'GET', 'PATCH', 'POST', 'PUT')
from .liteapi import liteapi
from .BaseAPIRequest import BaseAPIRequest, APIAuth, addResponse
from .APIModel import APIModel