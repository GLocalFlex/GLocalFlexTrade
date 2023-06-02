# Plugin for logging
from logging import INFO

from flxtrd.core.logger import log
from flxtrd.core.plugins.base import BasePlugin


class LoggingPlugin(BasePlugin):
    plugin_name = "LoggingPlugin"

    def before_request(self, method, url, headers, params, data):
        log(INFO, f"Making {method} request to {url}...")

    def after_request(self, response):
        log(INFO, f"Received response with status code: {response.status_code}")

    def __str__(self):
        return self.plugin_name
