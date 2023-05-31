from dataclasses import dataclass
from typing import List, Optional
import requests

@dataclass
class Device:
    """Device dataclass for storing device data and their access keys."""
    deviceName: Optional[str] = None
    deviceId: Optional[str] = None
    accessToken: Optional[str] = None
    appKey: Optional[str] = None

@dataclass
class User:
    """User dataclass for storing user data for authencation and registered devices."""
    name: str
    password: str
    accessToken: Optional[str] = None
    appKey: Optional[str] = None
    userId: Optional[str] = None
    devices: Optional[List[Device]] = None

@dataclass
class Broker:
    """RabbitMQ Broker dataclass for storing broker data."""
    ip: str
    port: str
    tickeroutexname :str = "ticker-out"
    exchangename: str = "in"

@dataclass
class Market:
    """Marketplace dataclass for storing marketplace data."""
    ip: str
    broker: Broker
    port: int = 443

@dataclass
class APIResponse:
    """APIResponse dataclass for storing the response from the API and the plugin data."""
    request_response: requests.Response
    plugin_data:  Optional[dict] = None


class FlexError(Exception):
    """GLocalflex basic error class."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f'{self.message}'