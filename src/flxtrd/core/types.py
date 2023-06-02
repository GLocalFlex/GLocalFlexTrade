import enum
from dataclasses import dataclass
from typing import List, Optional

import requests


class OrderType(str, enum.Enum):
    """Specifies the order types that can be placed on the market

    Terminology:

    OrderType.ASK creates a sell order to the market

    OrderType.BID creates a buy order to the market

    """

    ASK = "ask"  # sell order
    BID = "bid"  # buy order


@dataclass
class Flexibility:
    """Specifies the tradable good that is sold or bought on the marketplace

    wattage: float
    startime: int
    duration: int

    """

    wattage: float
    starttime: int
    duration: int
    expirationtime: int
    # TODO call as init method
    energy: float = 0

    @staticmethod
    def to_energy(wattage, duration):
        return wattage * (duration / (60 * 60 * 1000))


@dataclass
class Device:
    """Device dataclass for storing device data and their access keys."""

    deviceName: Optional[str] = None
    deviceId: Optional[str] = None
    accessToken: Optional[str] = None
    appKey: Optional[str] = None


@dataclass
class User:
    """User dataclass for storing user data for authencation and registered devices.
    """

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
    port: int = 5671
    tickeroutexname: str = "ticker-out"
    exchangename: str = "in"


@dataclass
class Market:
    """Marketplace dataclass for storing marketplace data."""

    ip: str
    broker: Broker
    port: int = 443


@dataclass
class MarketOrder:
    """Maket order type to create sell or buy orders

    The market order contains the tradable flexibility.

    type: OrderType
    price: float
    flexibility: Flexibility
    """

    type: OrderType
    price: float
    flexibility: Flexibility


@dataclass
class APIResponse:
    """APIResponse dataclass for storing the response from the API and the plugin data.
    """

    request_response: requests.Response
    plugin_data: Optional[dict] = None


class FlexError(Exception):
    """GLocalflex basic error class."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.message}"
