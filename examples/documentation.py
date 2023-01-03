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
    return username=='user' and password=='pass'

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