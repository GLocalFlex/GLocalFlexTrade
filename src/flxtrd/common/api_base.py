from abc import ABC, abstractmethod

class APIClient(ABC):
    def __init__(self, base_url):
        self.base_url = base_url
        self.plugins = []

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    @abstractmethod
    def make_request(self, method, endpoint, **kwargs):
        pass
