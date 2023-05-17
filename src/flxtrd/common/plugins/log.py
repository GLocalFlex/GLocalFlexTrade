# Plugin for logging
from flxtrd.common.plugins.base import APIplugin

class LoggingPlugin(APIplugin):
    def before_request(self, method, url, headers, params, data):
        print(f"Making {method} request to {url}...")

    def after_request(self, response):
        print(f"Received response with status code: {response.status_code}")
