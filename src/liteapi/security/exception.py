from ..exception import FORBIDDEN_ERROR, UNAUTHORIZED_ERROR, BAD_REQUEST_ERROR

BASE_OAUTH_ERROR = lambda error, **kwargs: BAD_REQUEST_ERROR(error=error, **{key: val for key, val in kwargs.items() if key in ['error_description', 'error_uri']})
INVALID_REQUEST_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='invalid_request', **kwargs)
INVALID_CLIENT_ERROR = lambda **kwargs: UNAUTHORIZED_ERROR({'WWW-Authenticate': 'Basic'}, error='invalid_client', **{key: val for key, val in kwargs.items() if key in ['error_description', 'error_uri']})
INVALID_GRANT_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='invalid_grant', **kwargs)
INVALID_SCOPE_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='invalid_scope', **kwargs)
UNAUTHORIZED_CLIENT_ERROR = lambda **kwargs: BASE_OAUTH_ERROR(error='unauthorized_client', **kwargs)
UNSUPPORTED_GRANT_TYPE = lambda **kwargs: BASE_OAUTH_ERROR(error='unsupported_grant_type', **kwargs)

def TOKEN_ERROR(**kwargs):
    www_authenticate_params = ['{}="{}"'.format(k, v) for k,v in kwargs.items() if k in ['realm', 'error', 'error_description']]
    if 'scope' in kwargs:
        www_authenticate_params.append('scope="{}"'.format(kwargs['scope'] if isinstance(kwargs['scope'], str) else ' '.join(kwargs['scope'])))
    return UNAUTHORIZED_ERROR({'WWW-Authenticate': 'Bearer' + (' ' + ','.join(www_authenticate_params)) if www_authenticate_params else ''})

INVALID_TOKEN_ERROR = lambda **kwargs: TOKEN_ERROR(error='invalid_token', **kwargs)
INSUFFICIENT_SCOPE_ERROR = lambda **kwargs: FORBIDDEN_ERROR(error='insufficient_scope', **kwargs)