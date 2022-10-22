from liteapi import liteapi,BaseAPIRequest

app = liteapi()

@app.register('/')
class rootMethod (BaseAPIRequest):
    def get(self):
        return {'message': 'Thank you for using liteapi'}

@app.register('/modules/{module}')
class moduleMethod (BaseAPIRequest):
    def post(self, module:str):
        return {'module': module}

app.run()