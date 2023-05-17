from abc import ABC, abstractmethod

class APIplugin(ABC):
    def __init__(self, base_url):
        pass

    @abstractmethod
    def before_request(self, method: str = None,
                    url: str = None,
                    headers = None,
                    params = None,
                    data = None):
        pass

    @abstractmethod
    def after_request(self,response: str | dict = None):
        pass