import traceback
from liteapi._internals import _headerDict, _mediaDict, _params_parser, _parse_content_type

fail = lambda msg: f'{msg} \033[91mFail\033[0m'
success = lambda msg: f'{msg} \033[92mSucceed\033[0m'

def test(_test, _msg = ''):
    assert _test, fail(_msg)
    print(success(_msg))

def tryCallable(cls, *args, **kwargs):
    try:
        cls(*args, **kwargs)
    except:
        traceback.print_exc()
        return False
    return True

def tryFailCallable(cls, *args, **kwargs):
    try:
        cls(*args, **kwargs)
    except:
        return True
    return False

def test_headerDict():
    try:
        print("Testing _headerDict class")
        test(tryCallable(_headerDict), 'Creating _headerDict object')
        myDict = _headerDict()
        test(hasattr(myDict, '_lowerKeys') and isinstance(myDict._lowerKeys, dict), 'Cheking _headerDict object init')
        myDict['Key1'] = 'value'
        test('key1' in myDict and 'KeY1' in myDict, 'Checkin key as case insensitive _headerDict object')
        test([*myDict.keys()][0] == 'Key1', 'Actual key name maintained under _headerDict object')
        myDict.update({'keY1': 'value', 'Key2': 'value'})
        test(len(myDict) == 2, 'Updating _headerDict object')
        test([*myDict.keys()][0] == 'keY1', 'Actual key name updated under _headerDict object')
        test(tryCallable(_headerDict, myDict), 'Creating _headerDict object with other dict as parameter')
        myDict2 = _headerDict(myDict)
        test(myDict2['KEY2'] == 'value', 'Copying _headerDict object')
        del myDict2['key2']
        test('Key2' not in myDict2 and 'key2' not in myDict2, 'Deleting key _headerDict object')
        myDict.clear()
        test(len(myDict) == 0 and 'key1' not in myDict, 'Testing _headerDict object')
    except:
        traceback.print_exc()
        return False
    return True

def test_mediaDict():
    try:
        print("Testing _mediaDict class")
        test(tryCallable(_mediaDict), 'Creating _mediaDict object')
        myDict = _mediaDict()
        test(tryFailCallable(myDict.__setitem__, 'test', 'value'), 'Exceprion raised for setting Invalid key for _mediaDict object')
        test(tryCallable(myDict.__setitem__, 'text/plain', 'value'), 'Setting valid media type format for _mediaDict object')
        test('test/javascript' not in myDict, 'Cheking for undefined mediatype in _mediaDict object')
        myDict['text/*'] = 'text*'
        test('text/css' in myDict and myDict['text/css'] == 'text*', 'Cheking for if text/css will get text/* media type in _mediaDict object')
        myDict['*/*'] = '**'
        test('application/json' in myDict and myDict['application/json'] == '**', 'Cheking for if application/json will get */* media type in _mediaDict object')
    except:
        traceback.print_exc()
        return False
    return True

def test_params_parser():
    try:
        print('Testing _params_parser function')
        test(tryCallable(_params_parser, ["test=test1", "test2=test123=2&test"]), 'Testing calling _params_parser function')
        myDict = _params_parser(["test=test1", "test2=test123=2&test"])
        test(len(myDict) == 2 and myDict['test2'] == 'test123=2&test', 'Test parsing parameters with _params_parser function')
    except:
        traceback.print_exc()
        return False
    return True

def test_parse_content_type():
    try:
        print('Testing _parse_content_type function')
        test(tryCallable(_parse_content_type, 'text/javascript'), 'Testing calling _parse_content_type function')
        contenttype, params = _parse_content_type('text/html; charset=utf-8')
        test(contenttype == 'text/html' and params['charset'] == 'utf-8', 'Test parsing contenttype with _parse_content_type function')
    except:
        traceback.print_exc()
        return False
    return True

test(test_headerDict(), 'Testing _headerDict class')
test(test_mediaDict(), 'Testing _mediaDict class')
test(test_params_parser(), 'Testing _params_parser function')
test(test_parse_content_type(), 'Testing _parse_content_type function')