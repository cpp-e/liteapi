# Examples

Here are some examples of how to use LiteAPI:

## Example 1: Getting Started

In this example, we create two API endpoints using the `liteapi` class and the `BaseAPIRequest` class.

```python
from liteapi import liteapi, BaseAPIRequest

app = liteapi()

@app.register('/')
class rootMethod(BaseAPIRequest):
    def get(self):
        return {'message': 'Thank you for using liteapi'}

@app.register('/modules/{module}')
class moduleMethod(BaseAPIRequest):
    def post(self, module: str):
        return {'module': module}

app.run()
```

## Example 2: Handling Query String

In this example, we create an API endpoint that handles query string parameters in the URL.

```python
from liteapi import liteapi, BaseAPIRequest

app = liteapi()

@app.register('/')
class rootMethod(BaseAPIRequest):
    def get(self):
        '''
        Query string parameters can be accessed using the dictionary self.request.query_string
        '''
        if 'who' in self.request.query_string:
            return {'message': f'Thank you {self.request.query_string["who"]} for using liteapi'}
        else:
            return {'message': 'Please introduce yourself using ?who=yourname in the URL'}

app.run()
```

## Example 3: Handling JSON Request

In this example, we create an API endpoint that handles a JSON request body.

```python
from liteapi import liteapi, BaseAPIRequest

app = liteapi()

'''
Test with request body content-type: application/json and json content:
{
    "who": "yourname"
}
'''

@app.register('/')
class rootMethod(BaseAPIRequest):
    def post(self):
        '''
        Request JSON can be accessed using the self.request.json
        '''
        if 'who' in self.request.json:
            return {'message': f'Thank you {self.request.json["who"]} for using liteapi'}
        else:
            return {'message': 'Please introduce yourself by adding the who parameter in the request body JSON data'}

app.run()
``` 

## Example 4: Using Verifiers

In this example, we create API endpoints that use verifiers to validate the data received in the request.

```python
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
    key: pattern('^[a-zA-Z]{3}-[0-9]{5}$')
    secret: Optional[str]

class returnedModule(APIModel):
    module: str
    key: str

@app.register('/modules/{module}')
class moduleMethod (BaseAPIRequest):
    def post(self, module:str, data:module) -> returnedModule:
        return returnedModule({'module': module, 'key': data.key})

app.run()
```

## Example 5: Handling Security

In this example, we created an app with SSL enabled, moreover we demonstrate the use of `RequireBasicAuth`, `RequireOAuth2PasswordAuth`, and `RequireOAuth2Token` for authentication, and the use of `APIAuth` class to get the authentication information in methods:
```python
from liteapi import liteapi,BaseAPIRequest,APIAuth
from liteapi.security import RequireBasicAuth, RequireOAuth2PasswordAuth, RequireOAuth2Token

#if ssl key file doesn't require password remove ssl_keypassword="password"
app = liteapi(host="0.0.0.0", port=443, ssl_certfile="cert.pem", ssl_keyfile="key.pem", ssl_keypassword="password")

@app.register('/basic')
class rootMethod (BaseAPIRequest):
    @RequireBasicAuth(checkerFunc=lambda username, password: username=="user" and password=="secret")
    def get(self, auth:APIAuth):
        return {'message': f'Thank you {auth.username} for using liteapi'}

@app.register('/token')
class tokenMethod (BaseAPIRequest):
    @RequireOAuth2PasswordAuth(checkerFunc=lambda username, password: username=="user" and password=="secret")
    def post(self):
        return {'access_token': 'mytoken', 'token_type': 'Bearer'}

@app.register('/OAuth')
class dataMethod (BaseAPIRequest):
    @RequireOAuth2Token(checkerFunc=lambda access_token: access_token == 'mytoken', token_url='token')
    def get(self):
        return {'message': f'Thank you for using liteapi'}

app.run()
```

## Example 6: Handling documentation module

In this example, we demonstrate how provide content to the documentation and the use of `Annotate` and `addResponse` decorators to provide detailed documentation for the API endpoints.

```python
from typing import Optional
from liteapi import liteapi,BaseAPIRequest,APIModel, addResponse
from liteapi.security import RequireBasicAuth
from liteapi.docs import Annotate

app = liteapi()

class ReturnedMassage(APIModel):
    message:Annotate(str, doc="This is a discription for this attribute", example="Welcome")

class Tenant(APIModel):
    tenant:Annotate(str, doc="This is a discription for this attribute", example="main")
    count:Optional[int]

@app.register('/')
class rootMethod (BaseAPIRequest):
    def get(self) -> ReturnedMassage: #adding a return class will help the documentation to add example for the response
        '''
        /breif: This should be a one line and it will be presented beside the api path
        This will be presented as implementation note where you could put full discription
        what to expect from this route. Even if it is broken to multiline it will still
        show as one line when rendered. To add a line break you must add the tag
        &lt;br&gt;.<br>Using this tag you can start writing on a new line.
        '''
        return ReturnedMassage({'message': 'Welcome'})

@app.register('/tenants/{tenant:str}')
class tenantMethod(BaseAPIRequest):
    @addResponse(200, "Successfull Response", ReturnedMassage)
    def get(self, tenant:Annotate(str, doc="This is the description of the parameter", example="main")): #the example of the parameter will be set as a default value
        '''
        parameter tenant will be added as a field in the documentation whic can be filled for the
        tryout
        '''
        return ReturnedMassage({'message': f'Welcome to {tenant}'})

    @addResponse(200, "Successfull Response", ReturnedMassage)
    @addResponse(202, "Accepted Tenant", Tenant)
    def post(self, tenant:Annotate(str, doc="This is the description of the parameter", example="main"), body:Tenant): #Annotating body class is not supported, but an example will be build automatically
        '''
        Users can expect different return models with different status codes if required
        by adding multiple addResponse decorators
        '''
        if tenant == "main":
            body.count = 15
            return body
        return ReturnedMassage({'message': 'Welcome'})

def checkuser(username, password):
    return username=='user'  and  password=='pass'

@app.register('/tenants/{tenant:str}/people/{id:int}')
class peopleMethod(BaseAPIRequest):
    @RequireBasicAuth(checkuser, realm='viewers')
    def get(self, tenant, id) -> ReturnedMassage:
        '''
        When Authentication is requred a lock button will be added to the documentation
        that the user can click to authenticate to try the API.
        '''
        return {'message': f'Welcome to {tenant}, You are viewing person with ID {id}'}

app.run()
```