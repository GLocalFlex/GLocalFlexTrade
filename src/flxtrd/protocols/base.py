from abc import ABC, abstractmethod


class BaseAPI(ABC):
    """Base class for public API interface"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    def send_request(self, **kwargs) -> dict:
        pass
