def RequireAuth(authFunc):
    def AuthFunction(checkerFunc, **kwargs):
        supported_methods = ['DELETE', 'GET', 'POST', 'PUT']
        def inner(requestClassorMethod):
            if isinstance(requestClassorMethod, type):
                if not requestClassorMethod._BaseAPIRequest__methods:
                    requestClassorMethod._BaseAPIRequest__methods = {}
                if not requestClassorMethod._BaseAPIRequest__methods_keys:
                    requestClassorMethod._BaseAPIRequest__methods_keys = []
                for method in supported_methods:
                    if method not in requestClassorMethod._BaseAPIRequest__methods and method.lower() in dir(requestClassorMethod):
                        requestClassorMethod._BaseAPIRequest__methods[method] = authFunc(getattr(requestClassorMethod, method.lower()), checkerFunc, **kwargs)
                        requestClassorMethod._BaseAPIRequest__methods_keys.append(method)
                return requestClassorMethod
            
            elif callable(requestClassorMethod):
                funname = requestClassorMethod.__name__
                if funname.upper() in supported_methods:
                    return authFunc(requestClassorMethod, checkerFunc, **kwargs)

        return inner
    return AuthFunction