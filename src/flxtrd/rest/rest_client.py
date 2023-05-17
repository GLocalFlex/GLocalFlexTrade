import requests
from flxtrd.common.api_base import APIClient
# HTTP REST implementation of the client

class RestAPIClient(APIClient):
    def make_request(self, method, endpoint, **kwargs):
        url = self.base_url + endpoint
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', {})
        data = kwargs.get('data', {})

        for plugin in self.plugins:
            plugin.before_request(method, url, headers, params, data)

        # Make HTTP request using a library of your choice (e.g., requests)
        response = requests.request(method, url, headers=headers, params=params, data=data)

        for plugin in self.plugins:
            plugin.after_request(response)

        return response
