# liteapi
Lite Python API Framework

## Usage
```python
from liteapi import liteapi,BaseAPIRequest

app = liteapi()

@app.register('/')
class rootMethod (BaseAPIRequest):
    def get(self):
        return {'message': 'Hello'}

app.run()
```