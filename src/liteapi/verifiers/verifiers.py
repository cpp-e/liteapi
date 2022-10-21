class _GenericVerifierAlias:
    def __init__(self, origin, params, callable = False, name = None, checkerFunction = None, paramc = None):
        self.__origin__ = origin
        self._checkerFunc = checkerFunction
        if not name:
            self.__module__ = origin.__module__
        self._name = name if name else repr(self.__origin__)
        if not isinstance(params, tuple):
            params = (params,)
        if paramc and paramc != len(params):
            raise Exception(f'{self._name} expect {paramc} parameters, received {len(params)}')
        self.__parameters__ = params
        self._callable = callable
    def __repr__(self):
        repr = self._name
        if self.__parameters__:
            params = tuple(f'"{p}"' if isinstance(p, str) else str(p) for p in self.__parameters__)
            if self._callable:
                repr += '(' + ', '.join(params) + ')'
            else:
                repr += '[' + ', '.join(params) + ']'
        return repr
    @property
    def args(self):
        return self.__parameters__
    
    def __call__(self, obj):
        if self._checkerFunc(self, obj):
            return obj
        raise Exception(f'Unable to initialize {self._name}, Invalid parameter')
    
    def __instancecheck__(self, obj):
        return self._checkerFunc(self, obj)

class VerifierClass:
    __slots__ = ('_name', '_argc', '_args', '_callable', '__call__', '__getitem__', '_checkerFunc')
    def __init__(self, name, argc = None, callable=False, checkerFunction = None):
        self._name = name
        self._argc = argc
        self._callable = callable
        if callable:
            self.__call__ = lambda *args: _GenericVerifierAlias(self, args, self._callable, checkerFunction=checkerFunction, paramc=argc)
        else:
            self.__getitem__ = lambda args: _GenericVerifierAlias(self, args, self._callable, checkerFunction=checkerFunction, paramc=argc)
    def __repr__(self):
        return self._name

def checkRange(self, obj):
    argtypes = None
    for a in self.args:
        if not argtypes and isinstance(a, int):
            argtypes = int
        elif argtypes != float and isinstance(a, float):
            argtypes = float
        elif not isinstance(a, (int, float)):
            argtypes = None
            break
    return argtypes and isinstance(obj, (int, argtypes)) and obj >= self.args[0] and obj <= self.args[1]

Range = VerifierClass('Range', 2, callable=True, checkerFunction=checkRange)
In = VerifierClass('In', checkerFunction=lambda self, obj: obj in self.args)
Max = VerifierClass('Max', 1, callable=True, checkerFunction=lambda self, obj: obj <= self.args[0])
Min = VerifierClass('Max', 1, callable=True, checkerFunction=lambda self, obj: obj >= self.args[0])