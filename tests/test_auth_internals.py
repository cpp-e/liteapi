from test_common import *
from liteapi.security import *

def checker(username, password):
    return username == 'user' and password == 'pass'

def test_basicAuth():
    try:
        print('Testing RequireBasicAuth')
        @RequireBasicAuth(checker, realm='tester')
        def get():
            pass
        test(hasattr(get, 'authenticator'), 'Check if method object is created')
        test(get.authenticator.__name__ == 'basic', 'Check if authenticator name is correct')
        test('realm' in get.authenticator._args and get.authenticator._args['realm'] == 'tester', 'Check if args are stored in authenticator object')
        test(get.authenticator._checker('user', 'pass'), 'Check if checker function is accessible through authenticator object')
    except:
        traceback.print_exc()
        return False
    return True

def test_digestAuth():
    try:
        print('Testing RequireDigestAuth')
        @RequireDigestAuth(checker, realm='tester')
        def get():
            pass
        test(hasattr(get, 'authenticator'), 'Check if method object is created')
        test(get.authenticator.__name__ == 'digest', 'Check if authenticator name is correct')
        test('realm' in get.authenticator._args and get.authenticator._args['realm'] == 'tester', 'Check if args are stored in authenticator object')
        test(get.authenticator._checker('user', 'pass'), 'Check if checker function is accessible through authenticator object')
    except:
        traceback.print_exc()
        return False
    return True

def test_oAuth2Password():
    try:
        print('Testing RequireOAuth2PasswordAuth')
        @RequireOAuth2PasswordAuth(checker, realm='tester')
        def get():
            pass
        test(hasattr(get, 'authenticator'), 'Check if method object is created')
        test(get.authenticator.__name__ == 'OAuth2', 'Check if authenticator name is correct')
        test('realm' in get.authenticator._args and get.authenticator._args['realm'] == 'tester', 'Check if args are stored in authenticator object')
        test(get.authenticator._checker('user', 'pass'), 'Check if checker function is accessible through authenticator object')
    except:
        traceback.print_exc()
        return False
    return True

def test_oAuth2Token():
    try:
        print('Testing RequireOAuth2Token')
        @RequireOAuth2Token(checker, realm='tester')
        def get():
            pass
        test(hasattr(get, 'authenticator'), 'Check if method object is created')
        test(get.authenticator.__name__ == 'OAuth2', 'Check if authenticator name is correct')
        test('realm' in get.authenticator._args and get.authenticator._args['realm'] == 'tester', 'Check if args are stored in authenticator object')
        test(get.authenticator._checker('user', 'pass'), 'Check if checker function is accessible through authenticator object')
    except:
        traceback.print_exc()
        return False
    return True

def all():
    test(test_basicAuth(), 'Testing RequireBasicAuth')
    test(test_digestAuth(), 'Testing RequireDigestAuth')
    test(test_oAuth2Password(), 'Testing RequireOAuth2PasswordAuth')
    test(test_oAuth2Token(), 'Testing RequireOAuth2Token')

all()