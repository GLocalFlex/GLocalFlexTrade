# Example usage of the client library
from src import AuthPlugin, LoggingPlugin
from src import RestAPIClient
import fxtrd

# Example usage of the client library
# Creating an instance of the REST API client
rest_api_client = RestAPIClient("https://api.example.com")

# Adding plugins to the REST API client
rest_api_client.add_plugin(AuthPlugin(app_token="YOUR_APP_TOKEN"))
rest_api_client.add_plugin(LoggingPlugin())

# Making requests using the REST API client
rest_response = rest_api_client.make_request("GET", "/users/")
print(rest_response.json())
