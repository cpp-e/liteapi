from typing import Union

# Internal Helper Classes
class _iuList(list):
    '''Unique case insinsitive list'''
    _lower = None
    def __init__(self, Iterable = None):
        self._lower = []
        if Iterable:
            [self._lower.append(i.lower()) for i in Iterable if (isinstance(i, str) and i.lower() not in self._lower)]
            super().__init__(Iterable)
        else:
            super().__init__()
    def __contains__(self, __o):
        return self._lower.__contains__(__o.lower())
    def append(self, __object):
        if not isinstance(__object, str) or __object.lower() in self._lower:
            return
        self._lower.append(__object.lower())
        super().append(__object)
    def clear(self):
        self._lower.clear()
        super().clear()
    

class _headerDict(dict):
    _lowerKeys = None
    def __init__(self, *args, **kwargs):
        self._lowerKeys = {k.lower():k for k,v in args[0].items()} if len(args) == 1 and isinstance(args[0], dict) else {}
        super().__init__(*args, **kwargs)
    def __getitem__(self, __key):
        return super().__getitem__(self._lowerKeys[__key.lower()])
    def __setitem__(self, __key, __value):
        if self._lowerKeys.__contains__(__key.lower()):
            super().__delitem__(self._lowerKeys[__key.lower()])
        self._lowerKeys[__key.lower()] = __key
        super().__setitem__(__key, __value)
    def __contains__(self, __o):
        return self._lowerKeys.__contains__(__o.lower())
    def __delitem__(self, __key):
        super().__delitem__(self._lowerKeys[__key.lower()])
        self._lowerKeys.__delitem__(__key.lower())
    def update(self, __m):
        for k in __m:
            if self._lowerKeys.__contains__(k.lower()):
                super().__delitem__(self._lowerKeys[k.lower()])
            self._lowerKeys[k.lower()] = k
        super().update(__m)
    def clear(self):
        self._lowerKeys.clear()
        super().clear()

class _mediaDict(dict):
    def __getitem__(self, __key):
        _type,_subtype = __key.lower().split('/')
        if super().__contains__(f'{_type}/{_subtype}'):
            return super().__getitem__(f'{_type}/{_subtype}')
        elif super().__contains__(f'{_type}/*'):
            return super().__getitem__(f'{_type}/*')
        elif super().__contains__('*/*'):
            return super().__getitem__(f'*/*')
        return super().__getitem__(__key)
    def __setitem__(self, __key, __value):
        if '/' not in __key:
            raise Exception('Invalid mimetype name: expect type/subtype')
        super().__setitem__(__key.lower(), __value)
    def __contains__(self, __o):
        if '/' not in __o:
            raise Exception('Invalid mimetype name: expect type/subtype')
        _type,_subtype = __o.lower().split('/')
        return super().__contains__(f'{_type}/{_subtype}') or super().__contains__(f'{_type}/*') or super().__contains__('*/*')
    def __delitem__(self, __key):
        super().__delitem__(__key.lower())

# Internal Helper Methods

def _params_parser(arr):
    return {k.strip():v.strip() for k,v in [i.split('=', maxsplit=1) for i in arr]}

def _parse_content_type(arg):
    content_type = arg.split(';')
    return content_type[0].strip(), _params_parser(content_type[1:])

def _is_CTL_char(_chr):
    _ord = ord(_chr)
    return not (_ord > 31 and _ord != 127)

def _is_TEXT_char(_chr):
    return not _is_CTL_char(_chr)

def _is_separator_char(_chr):
    return _chr not in "()<>@,;:\\\"/[]?={} \t"

def _is_valid_token(_token):
    _valid = True
    for c in _token:
        if _is_CTL_char(c) or _is_separator_char(c):
            _valid = False
            break
    return _valid

def _is_valid_cookie_value_octet(_octet):
    return _is_TEXT_char(_octet) and _octet not in " \",;\\"

def _is_valid_cookie_path(_path):
    _valid = True
    for c in _path:
        if _is_CTL_char(c) or c == ";":
            _valid = False
            break
    return _valid

def _isUnion(obj):
    return hasattr(obj, '__origin__') and obj.__origin__ is Union

def _repr(obj):
    if isinstance(obj, type):
        return obj.__qualname__ if obj.__qualname__ != 'tuple' else 'list'
    if _isUnion(obj):
        isOptional = type(None) in obj.__args__
        args = " | ".join([_repr(t) for t in obj.__args__ if t is not type(None)])
        return f'Optional({args})' if isOptional else args
    return repr(obj)

def _isinstance(obj, cls):
    return isinstance(obj, cls.__args__) if _isUnion(cls) else isinstance(obj, cls)