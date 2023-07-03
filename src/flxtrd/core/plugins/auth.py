from operator import is_
import ssl
from dataclasses import dataclass
from logging import DEBUG, ERROR, INFO
import stat

import requests

from flxtrd.core.logger import log
from flxtrd.core.plugins.base import BasePlugin
from flxtrd.core.types import FlexMarket, FlexResponse, FlexUser


@dataclass
class AuthResponse:
    """Container for the Auth response"""

    user_id: str = None
    app_key: str = None
    access_token: dict = None
    is_authenticated: bool = False


class AuthPlugin(BasePlugin):
    """Plugin for authentication"""

    plugin_name = "AuthPlugin"

    def __init__(self, user: FlexUser,  market:FlexMarket, verify_ssl: bool = True, ) -> None:
        self.auth_server = market.market_url
        self.user = user
        self.verify_ssl = verify_ssl
        self.ssl_context = self._creat_ssl_context()

    def _creat_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context()
        if not self.verify_ssl:
            # accept self signed certificates
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

    def before_request(
        self,
        method: str = None,
        url: str = None,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
    ) -> None:
        if self.user.access_token is None:
            raise ValueError("User access_token is required")

        return self.validateApplicationToken(
            authServer=self.auth_server,
            accessToken=self.user.access_token,
            verify_ssl=self.verify_ssl,
        )

    def after_request(self, response: FlexResponse) -> None:
        pass

    # def auth_client(self, authServer: str, username: str, password: str, appKey: str
    # ) -> AuthResponse:
    #     AuthResponse(userId="", appKey="", appToken=appKey)

    #     username = self.user.email
    #     username = self.user.password
    #     authdata = {"email": username, "password": password}
    #     requests.post(authServer, data=authdata, timeout=1)
    #     pass

    def __str__(self):
        return self.plugin_name

    def authenticate_user(self, endpoint: str = "/users/login") -> AuthResponse:
        """Authenticate the user and return the auth response"""
        userauthurl = f"https://{self.auth_server}{endpoint}"
        authdata = {
            "email": self.user.name,
            "password": self.user.password,
        }
        response = requests.post(userauthurl, data=authdata, verify=self.verify_ssl)
        if not response.status_code == 200:
            log(
                ERROR,
                f"Location/measurement point/application auth failed with"
                f" response {response.status_code}",
            )

        log(INFO, "User successfully authenticated")
        json_response = response.json()
        user_id = json_response["userId"]
        if "locations" in json_response:
            for locs in json_response["locations"]:
                # TODO let user decide which metering point to use
                # Pick first application/Metering point
                app_key = locs["_id"]
                access_token = locs["token"]
                break

        return AuthResponse(user_id=user_id, app_key=app_key, access_token=access_token, is_authenticated=True)

    def validateApplicationToken(
        self,
        authServer: str,
        accessToken: str,
        endpoint: str = "/users/mptoken/",
        verify_ssl: bool = True,
    ) -> None:
        if self._isUserValidated():
            log(INFO, "User already validated")
            return
        else:
            log(INFO, "User not validated, validating now")
            
        appAuthUrl = f"https://{authServer}{endpoint}{accessToken}"
        response = requests.get(appAuthUrl, verify=verify_ssl)

        if response.status_code != 200:
            if response.status_code == 404:
                log(
                    ERROR,
                    f"Access token is invalid, failed to validate access token, . "
                    f"status code {response.status_code}, "
                    f"message: {response.content.decode()}, "
                )

                return AuthResponse(is_authenticated=False)


        self.user.user_id = response.json()["userId"]
        if "locations" in response.json():
            if len(response.json()["locations"]) > 0:
                self.user.app_key = response.json()["locations"][0]["_id"]
            else:
                self.user.app_key = None
                log(ERROR, f"Failed to validate accessToken {accessToken}")
                return

        log(INFO, "Application token successfully received and validated")
        return

    def _isUserValidated(self) -> bool:
        """Check if the user is validated based on exising appKey"""
        if self.user.app_key is None:
            return False
        return True
