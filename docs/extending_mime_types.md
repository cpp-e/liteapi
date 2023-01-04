# Extending LiteAPI Mime Type Support

LiteAPI provide the developer the ability to extend the supported mime-types. It provides two functions `extend_supported_request_content_types` and `extend_supported_response_content_types` where the first one is used to extend request support and the second one is used to extend response support. Check the below example to illustrate how to make LiteAPI support yaml type.
 
## Example: Handling YAML Request and Response

To handle YAML data in requests and responses, you will need to install the `pyyaml` library:

```bash
pip install pyyaml
``` 

Then, you can use the following code to add support for `application/x-yaml` content type in your LiteAPI application:

```python
import yaml
from liteapi import liteapi, BaseAPIRequest

# Create an instance of the LiteAPI app
app = liteapi()

# Define a function to parse YAML data from requests
def request_application_yaml(data, charset = 'utf-8'):
    return yaml.safe_load(data.decode(charset))

# Define a function to serialize and encode YAML data for responses
def response_application_yaml(data, charset = 'utf-8'):
    return yaml.dump(data).encode(charset)

# Add the functions to the list of supported request and response content types
app.extend_supported_request_content_types('application/x-yaml', request_application_yaml)
app.extend_supported_response_content_types('application/x-yaml', response_application_yaml)

# Create an API endpoint that returns the request data in YAML format
@app.register('/')
class YAMLEndpoint(BaseAPIRequest):
    def post(self):
        self.response['content-type'] = 'application/x-yaml'
        return self.request.data

# Run the app
app.run()
``` 

Now you can send and receive YAML data in your LiteAPI application.