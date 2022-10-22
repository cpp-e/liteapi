from liteapi import liteapi,BaseAPIRequest,APIModel
from liteapi.verifiers import Range,In,VerifierClass
from typing import Optional
import re

app = liteapi()

'''
Verifiers available are:
Test against datatypes: bool,int,float,str,list,dict
Test against Union args
Test against APIModel subclasses
Test against liteapi verifiers: In, Range, Max, Min, Max
Test against custom verifiers

Test with request body content-type: application/json and json content:
{
    "who": "your_name",
    "age": your_age,
    "role": "your_role"
}
'''

class identity(APIModel):
    who:str
    age:Range(18, 60)
    role:In["Manager", "Developer", "Tester"]

@app.register('/')
class rootMethod (BaseAPIRequest):
    def post(self, data:identity):
        '''
        Request JSON can be accessed using the data variable which will handle type verifivation
        '''
        return {'message': f'Thank you {self.request.json["who"]} for using liteapi. Based on the provided data you are {self.request.json["age"]} years old and your role is {self.request.json["role"]}'}


'''
To create custom verifier you must create an instance on class liteapi.verifiers.VerifierClass
In this example we need to use the annotation as a callable format: instancename(*args)
The checker function must take two arguments: self and the value that need to be verified
To access the argument passed to the annotation in the checker function call self.args variable  
'''
pattern = VerifierClass("pattern", callable=True, checkerFunction=lambda self, v: re.match(self.args[0], v))

class module(APIModel):
    key: pattern('[a-zA-Z]{3}-[0-9]{5}')
    secret: Optional[str]

class returnedModule(APIModel):
    module: str
    key: str

@app.register('/modules/{module}')
class moduleMethod (BaseAPIRequest):
    def post(self, module:str, data:module) -> returnedModule:
        return returnedModule({'module': module, 'key': data.key})

app.run()