from ..exception import FORBIDDEN_ERROR, UNAUTHORIZED_ERROR, BAD_REQUEST_ERROR
from ..APIModel import APIModel
from ..docs.annotate import Annotate
from typing import Optional

class OAUTH_Error(APIModel):
    error: Annotate(str, doc='Reason Code', example='invalid_request')
    error_description: Annotate(Optional[str], doc='Detailed description of the error', example='access_token received using multiple methods')
    error_uri: Annotate(Optional[str], doc='URI to the API documentation')

BASE_OAUTH_ERROR = lambda error, **kwargs: BAD_REQUEST_ERROR(OAUTH_Error({**{'error': error},**{key: val for key, val in kwargs.items() if key in ('error_description', 'error_uri')}}))
INVALID_REQUEST_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='invalid_request', **kwargs)
INVALID_CLIENT_ERROR = lambda **kwargs: UNAUTHORIZED_ERROR({'WWW-Authenticate': 'Basic'}, OAUTH_Error({**{'error': 'invalid_client'},**{key: val for key, val in kwargs.items() if key in ('error_description', 'error_uri')}}))
INVALID_GRANT_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='invalid_grant', **kwargs)
INVALID_SCOPE_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='invalid_scope', **kwargs)
UNAUTHORIZED_CLIENT_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='unauthorized_client', **kwargs)
UNSUPPORTED_GRANT_TYPE = lambda **kwargs: BASE_OAUTH_ERROR(error='unsupported_grant_type', **kwargs)

def TOKEN_ERROR(**kwargs):
    www_authenticate_params = ['{}="{}"'.format(k, v) for k,v in kwargs.items() if k in ('realm', 'error', 'error_description')]
    if 'scope' in kwargs:
        www_authenticate_params.append('scope="{}"'.format(kwargs['scope'] if isinstance(kwargs['scope'], str) else ' '.join(kwargs['scope'])))
    return UNAUTHORIZED_ERROR({'WWW-Authenticate': 'Bearer' + (' ' + ','.join(www_authenticate_params)) if www_authenticate_params else ''})

INVALID_TOKEN_ERROR = lambda **kwargs: TOKEN_ERROR(error='invalid_token', **kwargs)
INSUFFICIENT_SCOPE_ERROR = lambda **kwargs: FORBIDDEN_ERROR(error='insufficient_scope', **kwargs)