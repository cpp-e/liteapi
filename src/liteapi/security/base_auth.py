from .. import LITEAPI_SUPPORTED_REQUEST_METHODS, BaseAPIRequest
from ..BaseAPIRequest import APIMethod

def RequireAuth(authFunc):
    def AuthFunction(checkerFunc, **kwargs):
        def inner(requestClassorMethod):
            if isinstance(requestClassorMethod, type) and issubclass(requestClassorMethod, BaseAPIRequest):
                for methodnam in LITEAPI_SUPPORTED_REQUEST_METHODS:
                    if methodnam.lower() in dir(requestClassorMethod):
                        setattr(requestClassorMethod, methodnam.lower(), APIMethod.create(methodFunc=getattr(requestClassorMethod, methodnam.lower()), authFunc=authFunc(checkerFunc, **kwargs)))
                return requestClassorMethod
            
            elif callable(requestClassorMethod):
                funname = requestClassorMethod.__name__
                if funname.upper() in LITEAPI_SUPPORTED_REQUEST_METHODS:
                    return APIMethod(methodFunc=requestClassorMethod, authFunc=authFunc(checkerFunc, **kwargs))

        return inner
    return AuthFunction