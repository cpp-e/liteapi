import traceback

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