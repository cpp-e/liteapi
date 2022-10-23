<img src="https://github.com/cpp-e/liteapi/raw/main/media/liteapi-logo.png" alt="liteapi" style="max-width: 100%">

---

Lite Framework, Easy Coding, High Performance, No Dependencies, Tested for Production

## Features
* **Lite with no dependencies**
    * The framework built using standard python libraries and does not need third party pre-requisites.
* **Easy Code**
    * The framework designed to allow different levels of skillsets to use the code and learn it fast.
* **Supported**
    * Our team is committed to review, test and resolve any issues related to the framework interactively. Please don’t hesitate to submit your problem in github’s issue section.

## Requirements
Python 3.6+

## Installation
```bash
pip install liteapi
```

## Usage
```python
from liteapi import liteapi,BaseAPIRequest

app = liteapi()

@app.register('/')
class rootMethod (BaseAPIRequest):
    def get(self):
        return {'message': 'Thank you for using liteapi'}

app.run()
```
* Import the framework using
```python
from liteapi import liteapi,BaseAPIRequest
```
* Create an app instance of liteapi
```python
app = liteapi()
```
    Note: to change the socket binding you can pass the host and port arguments to liteapi as below
```python
app = liteapi(host='0.0.0.0', port=8080)
```
* Register class for each URI (The class has to be subclass from BaseAPIRequest)
```python
@app.register('/')
class rootMethod (BaseAPIRequest):
```
* Inside your class, define your methods of get, delete, post, put
```python
def get(self):
    return {'message': 'Welcome to liteapi'}
```
* Run your instance
```python
app.run()
```

## Example
The below example shows different method use cases for liteapi:
```python
@app.register('/{tenant:str}')
class tenantMethod (BaseAPIRequest):
    def get(self, tenant):
        return {'message': 'Hello', 'tenant': tenant, 'query': self.request.query_string}
    def put(self, tenant):
        return {'method': 'Put', 'tenant': tenant, 'json': self.request.json}
    def post(self, tenant):
        return {'method': 'Post', 'tenant': tenant, 'json': self.request.json}
    def delete(self, tenant):
        return {'method': 'Delete', 'tenant': tenant, 'json': self.request.json}
```

## License
This project is licensed under the terms of GPL-3.0 license.