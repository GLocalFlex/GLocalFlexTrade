import enum
import json
from dataclasses import dataclass
from typing import List, Optional

import requests

from flxtrd.core import utils

MILLI = 1000


class OrderType(str, enum.Enum):
    """Specifies the order types that can be placed on the market

    Terminology:

    OrderType.ASK creates a sell order to the market

    OrderType.BID creates a buy order to the market

    """

    ASK = "ask"  # sell order
    BID = "bid"  # buy order


class FlexResource:
    """Specifies the tradable good that is sold or bought on the marketplace

    wattage: float
    startime: int
    duration: int

    """

    def __init__(
        self,
        power_w: float,
        start_time_epoch_s: int,
        duration_min: int,
        order_expiration_min: int,  # time in minutes for order validity starting from start time
        energy_kwh: float = 0,
    ) -> None:
        self.power_w = power_w
        self.start_time_epoch_ms = start_time_epoch_s * MILLI
        self.duration_min = duration_min
        self.order_expiration_min = order_expiration_min

        self.expiration_time_epoch_ms = start_time_epoch_s * MILLI + utils.min_to_ms(
            order_expiration_min
        )
        self.energy_wh = self._to_energy(power_w, duration_min)

    @staticmethod
    def _to_energy(power_w, duration):
        return power_w * utils.min_to_hour(duration)

    def __str__(self) -> str:
        return json.dumps(self._format_human_readable(), indent=4)

    def _format_human_readable(self) -> dict:
        return {
            "power_w": round(self.power_w, 3),
            "energy_wh": round(self.energy_wh, 3),
            "start_time": utils.get_formatted_time(self.start_time_epoch_ms),
            "duration_min": self.duration_min,
            "expiration_time": utils.get_formatted_time(self.expiration_time_epoch_ms),
        }

    @property
    def as_dict_human_readable(self):
        return self._format_human_readable()


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
    resource: Flexibility
    """

    order_type: OrderType
    price_eur: float
    resource: FlexResource

    def __str__(self) -> str:
        return json.dumps(self._format_human_readable(), indent=4)

    def _format_human_readable(self) -> dict:
        market_dict = {
            "Order type:": self.order_type.name,
            "price_eur": round(self.price_eur, 5),
        }

        return {**market_dict, **{"FlexResource": self.resource.as_dict_human_readable}}


@dataclass
class APIResponse:
    """APIResponse dataclass for storing the response from the API and the plugin data."""

    request_response: requests.Response = None
    order_response: str = "Not implemented"
    plugin_data: Optional[dict] = None


class FlexError(Exception):
    """GLocalflex basic error class."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.message}"
