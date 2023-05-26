import requests
from typing import List, Optional

from flxtrd.core.plugins.base import BasePlugin
from flxtrd.protocols.base import BaseAPI

class RestAPI(BaseAPI):
    """REST API implementation that connects to public API"""
    
    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    def send_request(self, method: str,
                     endpoint: str,
                     params: Optional[dict] = None,
                     data: Optional[dict] = None,
                     **kwargs) -> dict:
        
        url = self.base_url + endpoint
        headers = kwargs.get('headers', {})
        params = kwargs.get('params', {})
        data = kwargs.get('data', {})
        print(self)
        print(f"Send Request to {self.base_url}")
        print(f"method: {method} url: {url} headers: {headers} params: {params} data: {data}")
        response = {"status": 200, "data":"successfully simulated a request"}
        # Make HTTP request using a library of your choice (e.g., requests)
        # response = requests.request(method, url, headers=headers, params=params, data=data)

        return response
