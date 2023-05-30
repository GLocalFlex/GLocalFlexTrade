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
class APIResponse:
    """APIResponse dataclass for storing the response from the API and the plugin data."""
    request_response: requests.Response
    plugin_data:  Optional[dict] = None