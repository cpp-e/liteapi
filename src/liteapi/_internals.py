from unicodedata import category
# Internal Helper Classes

class _headerDict(dict):
    def __getitem__(self, __key):
        return super().__getitem__(__key.lower())
    def __setitem__(self, __key, __value):
        super().__setitem__(__key.lower(), __value)
    def __contains__(self, __o):
        return super().__contains__(__o.lower())
    def __delitem__(self, __key):
        super().__delitem__(__key.lower())

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
    return _valid

def _is_valid_cookie_value_octet(_octet):
    return _is_TEXT_char(_octet) and _octet not in " \",;\\"

def _is_valid_cookie_path(_path):
    _valid = True
    for c in _path:
        if _is_CTL_char(c) or c == ";":
            _valid = False
    return _valid