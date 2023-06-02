from typing import Optional

import requests

from flxtrd.protocols.base import BaseAPI


class RestAPI(BaseAPI):
    """Example REST API class that uses the requests library to make HTTP requests"""

    def __init__(self, base_url: str):
        super().__init__(base_url=base_url)

    def send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        ssl: bool = True,
        verify_ssl: bool = True,
        **kwargs,
    ) -> dict:
        if ssl:
            url = f"https://{self.base_url + endpoint}"
        else:
            url = f"http://{self.base_url + endpoint}"

        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            verify=verify_ssl,
        )

        return response, self.check_status(response, url, endpoint)

    def check_status(self, response: requests.Response, url, endpoint) -> bool:
        """Checks the status code of the response"""
        if response.status_code == 200:
            return False
        elif response.status_code == 401:
            return "Authentication failed"
        elif response.status_code == 404:
            return f"{url} not found"
        elif response.status_code == 500:
            return f"""Internal server error, endpoint is correct but data or parameters might be wrong. Check the API documentation for endpoint {endpoint} """
