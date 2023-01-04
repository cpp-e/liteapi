# Handling Errors

To handle errors, developer can import the `APIException` class from `liteapi.exception` and raise errors as shown in the example below:

## Example

```python
from liteapi import liteapi,BaseAPIRequest,APIModel
from liteapi.exception import APIException

app = liteapi()

class Custom_Error(APIModel):
    error:str
    error_description:Optional[str]
    error_uri:Optional[str]

@app.register('/')
class moduleMethod (BaseAPIRequest):
    def get(self):
        '''
        This API is used to handle errors.
        To raise error, developer can use APIException provided by liteapi.
        APIException takes three parameters: 
        code: HTTP status code
        *args: status message, dictionary of response headers, and response body as an instance of a subclass of APIModel in this order
        **kwargs: named parameters that will be the content of the response body in json format.
        '''
        raise APIException(401, {'WWW-Authenticate': 'Basic'})

    def post(self):
        '''
        Raise error if request body is missing
        '''
        if self.request.json is None:
            raise APIException(400, Custom_Error({'error':'Bad Request'}))
        return {'message': 'Thanks for the request'} 

app.run()
```

To make the code more readable, liteapi provide different lambdas to handle different status codes, i.e. no need to pass the code as an parameter. The lambdas are:

- `BAD_REQUEST_ERROR`
- `UNAUTHORIZED_ERROR`
- `PAYMENT_REQUIRED_ERROR`
- `FORBIDDEN_ERROR`
- `NOT_FOUND_ERROR`
- `METHOD_NOT_ALLOWED_ERROR`
- `REQUEST_TIMEOUT_ERROR`
- `UNSUPPORTED_MEDIA_TYPE_ERROR`
- `TOO_MANY_REQUESTS_ERROR`
- `UNAVAILABLE_FOR_LEGAL_REASONS_ERROR`
- `INTERNAL_SERVER_ERROR_ERROR`
- `NOT_IMPLEMENTED_ERROR`
- `HTTP_VERSION_NOT_SUPPORTED_ERROR`
- `INSUFFICIENT_STORAGE_ERROR`

Example usage:
```python
raise UNAUTHORIZED_ERROR({'WWW-Authenticate': 'Basic'})
```