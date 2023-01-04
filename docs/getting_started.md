# Getting Started

To get started with LiteAPI, you'll need to import the `liteapi` module and the `BaseAPIRequest` class. You can do this with the following code:

```python
from liteapi import liteapi, BaseAPIRequest
``` 

Next, create an instance of the `liteapi` class. By default, LiteAPI will bind to the IP address `127.0.0.1` and port `8000`, but you can specify a different host and port by passing the `host` and `port` named parameters when initializing the `liteapi` app. For example:

```python
app = liteapi(host='0.0.0.0', port=8080)
``` 

To enable SSL for your API server, pass the `ssl_certfile`, `ssl_keyfile`, and `ssl_keypassword` named parameters when initializing the `liteapi` app. For example:

```python
app = liteapi(host='0.0.0.0', port=443, ssl_certfile='/path/to/certfile.pem', ssl_keyfile='/path/to/keyfile.pem', ssl_keypassword='keypassword')
``` 

To create a new API endpoint, you'll need to define a class that derives from `BaseAPIRequest`. This class can include methods for handling HTTP GET, POST, PUT, and DELETE requests. You can use the `app.register` decorator above the class to register it with your app and specify the URL path for the endpoint. Endpoint parameters are defined using curly braces (`{}`) in the URL path, followed by a colon (`:`) and the parameter datatype. The supported datatypes are `str`, `int`, `float`, and `path`. For example:

```python
@app.register('/tenants/{tenant_id:int}')
class TenantAPI(BaseAPIRequest):
    def get(self, tenant_id: int):
        return f'Retrieving tenant with ID {tenant_id}'
    
    def put(self, tenant_id: int):
        return f'Updating tenant with ID {tenant_id}'
    
    def delete(self, tenant_id: int):
        return f'Deleting tenant with ID {tenant_id}'
``` 

Alternatively, you can use the `app.register` decorator as a function and pass the endpoint class as an argument:

```python
class TenantAPI(BaseAPIRequest):
    def get(self, tenant_id: int):
        return f'Retrieving tenant with ID {tenant_id}'
    
    def put(self, tenant_id: int):
        return f'Updating tenant with ID {tenant_id}'
    
    def delete(self, tenant_id: int):
        return f'Deleting tenant with ID {tenant_id}'

app.register('/tenants/{tenant_id:int}')(TenantAPI)
``` 

To run the app, call the `app.run()` method:

```python
app.run()
``` 

By default, LiteAPI returns the response in `application/json` format. If the endpoint method returns a data of type `int`, `float`, `bool`, or `str`, the expected response will be `{"data": returned_data}`. If the method returns data of type `list` or `dict`, the data will be converted to JSON and returned as is.

For example, if the `get` method of the `TenantAPI` class returns the string `"Retrieving tenant with ID 123"`, the response will be:

```json
{"data": "Retrieving tenant with ID 123"}
``` 

If the `get` method returns a dictionary:

```python
def get(self, tenant_id: int):
    return {'tenant_id': tenant_id, 'name': 'Example Company'}
```

The response will be:

```json
{"tenant_id": 123, "name": "Example Company"}
```