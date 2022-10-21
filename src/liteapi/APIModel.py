from .verifiers.exception import *
from json import JSONEncoder
from typing import Union

def _isUnion(obj):
    return '__origin__' in obj.__dict__ and obj.__origin__ is Union

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
        return annotation(value)
    raise Exception('Invalid Type Object')

class APIModel:
    '''
    Base class for API Data
    '''
    def __init__(self, json_obj:dict):
        for a in json_obj:
            if a not in self.__annotations__:
                raise BAD_REQUEST_ERROR(error = "Invalid Parameter", error_description = f'reply from class "{self.__class__.__name__}": JSON object contains an invalid parameter: "{a}"')
        for a in self.__annotations__:
            if a not in json_obj:
                if _isUnion(self.__annotations__[a]) and isinstance(None, self.__annotations__[a].__args__):
                    self.__setattr__(a, None)
                else:
                    raise BAD_REQUEST_ERROR(error = "Invalid Parameter", error_description = f'reply from class "{self.__class__.__name__}": JSON object missing parameter: "{a}"')
            else:
                try:
                    self.__setattr__(a, _checkValue(self.__annotations__[a], json_obj[a]))
                except:
                    raise BAD_REQUEST_ERROR(error = "Invalid Parameter", error_description = f'reply from class "{self.__class__.__name__}": JSON object parameter "{a}" is of invalid type; expect {self.__annotations__[a]}')

class APIJSONEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__ if isinstance(o, APIModel) else super().default(o)