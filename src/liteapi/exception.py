from .errno import strerror
class APIException(Exception):
    def __init__(self, code, *args):
        self.code = code
        self.strerror = strerror(code)
        super().__init__(*args)