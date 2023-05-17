from flxtrd.common.plugins.base import APIplugin

# Plugin for authentication
class AuthPlugin(APIplugin):
    def __init__(self, app_token: str) -> None:
        self.app_token = app_token

    def before_request(self, method, url, headers, params, data) -> None:
        headers['Authorization'] = f"Bearer {self.app_token}"

    def after_request(self, response):
        pass