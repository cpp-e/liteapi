from liteapi import liteapi,BaseAPIRequest

app = liteapi()

@app.register('/')
class rootMethod (BaseAPIRequest):
    def get(self):
        '''
        QueryString parameters can be accessed using the dictionary self.request.query_string
        '''
        if 'who' in self.request.query_string:
            return {'message': f'Thank you {self.request.query_string["who"]} for using liteapi'}
        else:
            return {'message': f'Please introduce yourself using ?who=yourname in the URL'}

app.run()