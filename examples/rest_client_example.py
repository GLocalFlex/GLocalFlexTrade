# Example usage of the client library
from flxtrd import FlexAPIClient
from flxtrd import AuthPlugin, LoggingPlugin

# Example usage of the client library
# Creating an instance of the REST API client
# rest_api_client = RestAPIClient("https://api.example.com")

# # Adding plugins to the REST API client
# rest_api_client.add_plugin(AuthPlugin(app_token="YOUR_APP_TOKEN"))
# rest_api_client.add_plugin(LoggingPlugin())

# # Making requests using the REST API client
# rest_response = rest_api_client.make_request("GET", "/users/")
# print(rest_response.json())

def main():

    GFLEX_API_URL = "localhost"

    client = FlexAPIClient(base_url=GFLEX_API_URL)
    client.make_request(method="POST", endpoint="/user/login")
    client.add_plugin(AuthPlugin(app_token="secret"))
    client.make_request(method="POST", endpoint="/user/login")
    client.add_plugin(LoggingPlugin())


if __name__ == "__main__":
        main()