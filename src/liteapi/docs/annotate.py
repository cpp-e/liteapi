from .._internals import _repr, _isinstance
class _GenericAnnonateAlias:
    def __init__(self, origin, cls, doc, example):
        self.__origin__ = origin
        self._cls = cls
        self._doc = doc or ''
        self._name = _repr(cls)
        self._example = example or ''
        if example is not None and not _isinstance(example, cls):
            raise Exception(f'Invalid example for type {_repr(cls)}')

    def __repr__(self):
        return self._name

    @property
    def cls(self):
        return self._cls

    @property
    def doc(self):
        return self._doc

    @property
    def example(self):
        return self._example

    def __call__(self, obj):
        return self._cls(obj)

    def __instancecheck__(self, obj):
        return _isinstance(obj, self._cls)
    
    def __subclasscheck__(self, __subclass):
        return issubclass(__subclass, self._cls)
    
    def __eq__(self, __o):
        return __o == self._cls

class AnnotationClass:
    __slots__ = ('_name')
    def __init__(self, name):
        self._name = name
    def __repr__(self):
        return self._name
    def __call__(self, cls, doc = None, example = None):
        return _GenericAnnonateAlias(self, cls, doc, example)

Annotate = AnnotationClass('Annotate')

def isAnnotate(obj):
    return hasattr(obj, '__origin__') and obj.__origin__ is Annotate