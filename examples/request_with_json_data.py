from liteapi import liteapi,BaseAPIRequest

app = liteapi()

'''
Test with request body content-type: application/json and json content:
{
    "who": "yourname"
}
'''

@app.register('/')
class rootMethod (BaseAPIRequest):
    def post(self):
        '''
        Request JSON can be accessed using the self.request.json
        '''
        if 'who' in self.request.json:
            return {'message': f'Thank you {self.request.json["who"]} for using liteapi'}
        else:
            return {'message': f'Please introduce yourself by adding the who parameter in the request body JSON data'}

app.run()