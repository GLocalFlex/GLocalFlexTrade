from dataclasses import dataclass
from flxtrd.core.plugins.base import BasePlugin
from flxtrd.core.types import User
import requests
import ssl
from typing import Tuple
from flxtrd.core.logger import log
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL

@dataclass
class AuthResponse:
    """Container for the Auth response"""
    userId: str
    appKey: str
    appToken: dict

class AuthPlugin(BasePlugin):
    """ Plugin for authentication """

    plugin_name = "AuthPlugin"

    def __init__(self,
                 user: User,
                 authServer: str,
                 verify_ssl: bool = True) -> None:
        self.authServer = authServer
        self.user = user
        self.verify_ssl = verify_ssl
        self.ssl_context = self._creat_ssl_context()

    def _creat_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context()
        if not self.verify_ssl:
            # accept self signed certificates
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

    def before_request(self, method:str = None,
                       url = None,
                       headers = {},
                       params = {},
                       data = {}) -> None:
        
        if self.user.accessToken is not None:
            self.validateApplicationToken(authServer=self.authServer, accessToken=self.user.accessToken, verify_ssl=self.verify_ssl)

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
    
    
    def authClient(self,
                   endpoint: str = "/users/login") -> None:
        userauthurl = f'https://{self.authServer}{endpoint}'
        authdata = {'email':  self.user.username, 'password': self.user.password}
        response = requests.post(userauthurl, data=authdata)
        if response.status_code == 200:
            log(INFO, "USER AUTH SUCCESFULL")
            json_response = response.json()
            self.user.userId = json_response['userId']
            if 'locations' in json_response:
                for locs in json_response['locations']:
                    if self.user.appKey:
                        if self.user.appKey == locs['_id']:
                            self.user.accessToken = locs['token']
                            break
                    else:
                        #Pick first application/Metering point
                        self.user.appKey = locs['_id']
                        self.user.accessToken = locs['token']
                        break
        else:
            log(INFO, f'Location/measurement point/application auth failed with response {response.status_code}')


    def validateApplicationToken(self, 
                                 authServer: str,
                                accessToken: str,
                                endpoint: str = "/users/mptoken/",
                                verify_ssl: bool= True) -> Tuple[str, str]:
        appAuthUrl = f'https://{authServer}{endpoint}{accessToken}'
        response = requests.get(appAuthUrl, verify=verify_ssl)
        
        if not response.status_code == 200:
            log(ERROR, f"Response status code {response.status_code},"
                    f"failed to validate accessToken {accessToken}")
            return "", ""
        
        self.user.userId = response.json()['userId']
        if 'locations' in response.json().keys():
            if len(response.json()['locations']) > 0:
                self.user.appKey = response.json()['locations'][0]['_id']
            else:
                self.user.appKey = None
                log(ERROR, f'Failed to validate accessToken {accessToken}')
                return
        
        log(INFO, f'Access token successfully validated')
        return
