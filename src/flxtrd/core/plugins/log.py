# Plugin for logging
from flxtrd.core.plugins.base import BasePlugin

class LoggingPlugin(BasePlugin):

    plugin_name = "LoggingPlugin"
    def before_request(self, method, url, headers, params, data):
        print(f"Making {method} request to {url}...")

    def after_request(self, response):
        print(f"Received response with status code: {response.status_code}")

    def __str__(self):
        return self.plugin_name