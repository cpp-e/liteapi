from liteapi import liteapi,BaseAPIRequest,APIAuth
from liteapi.security import RequireBasicAuth, RequireOAuth2PasswordAuth, RequireOAuth2Token

app = liteapi()

@app.register('/basic')
class rootMethod (BaseAPIRequest):
    @RequireBasicAuth(checkerFunc=lambda username, password: username=="user" and password=="secret")
    def get(self, auth:APIAuth):
        return {'message': f'Thank you {auth.username} for using liteapi'}

@app.register('/token')
class rootMethod (BaseAPIRequest):
    @RequireOAuth2PasswordAuth(checkerFunc=lambda username, password: username=="user" and password=="secret")
    def post(self):
        return {'access_token': 'mytoken', 'token_type': 'Bearer'}

@app.register('/OAuth')
class rootMethod (BaseAPIRequest):
    @RequireOAuth2Token(checkerFunc=lambda access_token: access_token == 'mytoken')
    def get(self):
        return {'message': f'Thank you for using liteapi'}

app.run()