from .verifiers.exception import *
from .docs.annotate import isAnnotate
from ._internals import _repr,_isUnion, _isinstance
from json import JSONEncoder

def _checkValue(annotation, value):
    if isAnnotate(annotation):
        annotation = annotation.cls
    if annotation == float and isinstance(value, int):
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
                raise Exception(f'reply from class "{_repr(self.__class__)}": object contains an invalid parameter: "{a}"')
        for a in self.__annotations__:
            if a not in json_obj:
                if _isinstance(None, self.__annotations__[a]):
                    self.__setattr__(a, None)
                else:
                    raise Exception(f'reply from class "{_repr(self.__class__)}": object missing parameter: "{a}"')
            else:
                try:
                    self.__setattr__(a, _checkValue(self.__annotations__[a], json_obj[a]))
                except:
                    raise Exception(f'reply from class "{_repr(self.__class__)}": object parameter "{a}" is of invalid value; expect {_repr(self.__annotations__[a])}')

class APIJSONEncoder(JSONEncoder):
    def default(self, o):
        return {k:v for k,v in o.__dict__.items() if v is not None} if isinstance(o, APIModel) else super().default(o)