from liteapi import liteapi,BaseAPIRequest
#if ssl key file doesn't require password remove ssl_keypassword="password"
app = liteapi(host="0.0.0.0", port=443, ssl_certfile="cert.pem", ssl_keyfile="key.pem", ssl_keypassword="password")

@app.register('/')
class rootMethod (BaseAPIRequest):
    def get(self):
        return {'message': 'Thank you for using liteapi'}

@app.register('/modules/{module}')
class moduleMethod (BaseAPIRequest):
    def post(self, module:str):
        return {'module': module}

app.run()