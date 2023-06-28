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

    Attributes:
        power_w: float
            The power in Watt that is sold or bought on the marketplace
        start_time_epoch_s: int
            The start time of the flexibility in seconds since epoch
        duration_min: int
            The duration in minutes of the flexibility. Beginning from start_time_epoch_s.
        order_expiration_min: int
            The time in minutes for order validity starting from start_time_epoch_s.

    """

    def __init__(
        self,
        power_w: float,
        start_time_epoch_s: int,
        duration_min: int,
        order_expiration_min: int,  # time in minutes for order validity starting from start time
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
class FlexDevice:
    """Device dataclass for storing device data and their access keys.

    Attributes:
        deviceName: str
            The name of the device
        deviceId: str
            The device id
        accessToken: str
            The device access token
        appKey: str
            The app key
    """

    deviceName: Optional[str] = None
    deviceId: Optional[str] = None
    accessToken: Optional[str] = None
    appKey: Optional[str] = None


@dataclass
class FlexUser:
    """User dataclass for storing user data for authencation and registered devices."""

    name: str
    password: str
    access_token: Optional[str] = None
    app_key: Optional[str] = None
    user_id: Optional[str] = None
    devices: Optional[List[FlexDevice]] = None


@dataclass
class FlexBroker:
    """RabbitMQ Broker dataclass for storing broker data."""

    url: str
    port: int = 5671
    tickeroutexname: str = "ticker-out"
    exchangename: str = "in"


class FlexMarket:
    """Marketplace dataclass for storing marketplace data."""

    def __init__(
        self,
        market_url: str,
        market_port: int = 443,
        broker_url: str = None,
        broker_port: int = 5671,
    ) -> None:
        # TODO url deprecated
        self.url: str = market_url
        self.market_url: str = market_url
        self.port: int = market_port
        if broker_url is None:
            broker_url = market_url
        self.broker: FlexBroker = FlexBroker(url=broker_url, port=broker_port)


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
class FlexResponse:
    """APIResponse dataclass for storing the response from the API and the plugin data.

    Attributes:
        request_response: requests.Response
            The response from the REST API
        order_response: str
            The response from the market broker
        plugin_data: Optional[dict]
            The plugin data from the added plugins if any
    """

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
