from .verifiers.exception import *
from json import JSONEncoder
from typing import Union

def _isUnion(obj):
    return hasattr(obj, '__origin__') and obj.__origin__ is Union

def _repr(obj):
    if isinstance(obj, type):
        if obj.__module__ == 'builtins' or obj.__module__ == '__main__':
            return obj.__qualname__
        return f'{obj.__module__}.{obj.__qualname__}'
    if _isUnion(obj):
        return " | ".join([_repr(t) for t in obj.__args__])
    return repr(obj)

def _isinstance(obj, cls):
    return isinstance(obj, cls.__args__) if _isUnion(cls) else isinstance(obj, cls)

def _checkValue(annotation, value):
    if annotation is float and isinstance(value, int):
        return float(value)
    if _isUnion(annotation):
        for a in annotation.__args__:
            try:
                return _checkValue(a, value)
            except:
                pass
    elif isinstance(value, annotation) or \
         isinstance(annotation, type) and issubclass(annotation, APIModel) and isinstance(value, dict):
        return value is None or annotation(value)
    raise Exception('Invalid Type Object')

class APIModel:
    '''
    Base class for API Data
    '''
    def __init__(self, json_obj:dict):
        for a in json_obj:
            if a not in self.__annotations__:
                raise Exception(f'reply from class "{_repr(self.__class__)}": JSON object contains an invalid parameter: "{a}"')
        for a in self.__annotations__:
            if a not in json_obj:
                if _isinstance(None, self.__annotations__[a]):
                    self.__setattr__(a, None)
                else:
                    raise Exception(f'reply from class "{_repr(self.__class__)}": JSON object missing parameter: "{a}"')
            else:
                try:
                    self.__setattr__(a, _checkValue(self.__annotations__[a], json_obj[a]))
                except:
                    raise Exception(f'reply from class "{_repr(self.__class__)}": JSON object parameter "{a}" is of invalid value; expect {_repr(self.__annotations__[a])}')

class APIJSONEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__ if isinstance(o, APIModel) else super().default(o)