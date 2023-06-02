from abc import ABC, abstractmethod


class BasePlugin(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def before_request(
        self,
        method: str = None,
        url: str = None,
        headers=None,
        params=None,
        data=None,
    ):
        pass

    @abstractmethod
    def after_request(self, response: str | dict = None):
        pass

    @abstractmethod
    def __str__(self):
        pass
