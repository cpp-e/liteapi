from liteapi import liteapi,BaseAPIRequest
import yaml

app = liteapi()

def request_application_yaml(data, charset = 'utf-8'):
    return yaml.safe_load(data.decode(charset))

def response_application_yaml(data, charset = 'utf-8'):
    return yaml.dump(data).encode(charset)

app.extend_supported_request_content_types('application/x-yaml', request_application_yaml)
app.extend_supported_response_content_types('application/x-yaml', response_application_yaml)

@app.register('/')
class rootMethod (BaseAPIRequest):
    def get(self):
        return {'message': 'Thank you for using liteapi'}

@app.register('/modules/{module}')
class moduleMethod (BaseAPIRequest):
    def post(self, module:str):
        self.response['content-type'] = 'application/x-yaml'
        return {'module': module}

app.run()