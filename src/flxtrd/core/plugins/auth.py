from dataclasses import dataclass
from flxtrd.core.plugins.base import BasePlugin
import requests

@dataclass
class AuthResponse:
    """Container for the Auth response"""
    userId: str
    appKey: str
    appToken: dict

class AuthPlugin(BasePlugin):
    """ Plugin for authentication """

    plugin_name = "AuthPlugin"

    def __init__(self, app_token: str) -> None:
        self.app_token = app_token

    def before_request(self, method, url, headers, params, data) -> None:
        headers['Authorization'] = f"Bearer {self.app_token}"

    def after_request(self, response):
        pass

    def auth_client(authServer: str,
                    username: str,
                    password: str,
                    appKey: str)-> AuthResponse:
        
        auth_response = AuthResponse(userId="", appKey="", appToken=appKey)

        authdata = {'email': username, 'password': password}
        response = requests.post(authServer, data=authdata, timeout=1)
        pass

    def __str__(self):
        return self.plugin_name