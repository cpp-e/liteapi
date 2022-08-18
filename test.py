from liteapi import liteapi,BaseAPIRequest

app = liteapi()

@app.register('/')
class rootMethod (BaseAPIRequest):
    description = "This is a test root api"
    def get(self):
        return {'message': 'Hello'}

@app.register('/{tenant:str}')
class tenantMethod (BaseAPIRequest):
    description = "This is a test tenant api"
    def get(self, tenant):
        return {'message': 'Hello', 'tenant': tenant, 'query': self.request.query_string}
    def put(self, tenant):
        return {'method': 'Put', 'tenant': tenant, 'json': self.request.json}
    def post(self, tenant):
        return {'method': 'Post', 'tenant': tenant, 'json': self.request.json}
    def delete(self, tenant):
        return {'method': 'Delete', 'tenant': tenant, 'json': self.request.json}

@app.register('/{tenant:str}/{id:int}')
class tenantMethod (BaseAPIRequest):
    description = "This is a test tenant api"
    def get(self, tenant, id):
        return {'message': 'Hello', 'tenant': tenant, 'id': id}
    def post(self, tenant, id):
        return {'method': 'Delete', 'tenant': tenant, 'id': id, 'json': self.request.json}
    def delete(self, tenant, id):
        return {'method': 'Delete', 'tenant': tenant, 'id': id}

app.run()