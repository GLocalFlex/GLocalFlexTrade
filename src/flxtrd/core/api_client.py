from logging import DEBUG, INFO, WARNING
import sys
from typing import List, Optional, Tuple
from warnings import warn

from flxtrd.core.logger import log
from flxtrd.core.plugins.auth import AuthPlugin
from flxtrd.core.plugins.base import BasePlugin
from flxtrd.core.types import (
    FlexError,
    FlexMarket,
    FlexResponse,
    FlexUser,
    MarketOrder,
    OrderType,
)
from flxtrd.protocols.ampq import AmpqAPI
from flxtrd.protocols.base import BaseAPI
from flxtrd.protocols.restapi import RestAPI


class FlexAPIClient:
    """Example API Client that uses the api and auth plugin

    Params:
        user: User account configuration object
        market: Market configuration object
        request_protocol: Protocol used for communication with the Rest API
        trade_protocol: Protocol used for communication with the trading API
        plugins: List of plugins to use

    """

    def __init__(
        self,
        user: FlexUser,
        market: FlexMarket,
        base_url: str = None,
        request_protocol: BaseAPI = RestAPI,
        trade_protocol: AmpqAPI = AmpqAPI,
        plugins: List[BasePlugin] = [],
    ) -> None:
        if base_url is not None:
            warn(
                "Argument base_url is deprecated in favor of market.market_url v0.2.0",
                DeprecationWarning,
                stacklevel=2,
            )

        if user is None or market is None:
            raise TypeError("User and market must be provided")
        
        self.user = user
        self.market = market
        self.request_protocol = request_protocol(base_url=market.market_url)

        # By default the Auth Plugin is added
        self.plugins = plugins or [AuthPlugin(user=user, market=market)]

        self.trade_protocol: AmpqAPI = trade_protocol(
            base_url=market.market_url, user=user, broker=market.broker
        )

        self.context = None

    def send_order(
        self,
        market_order: MarketOrder,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        ssl: Optional[bool] = True,
        verify_ssl: Optional[bool] = True,
        **kwargs,
    ) -> Tuple[FlexResponse, FlexError | None]:
        """Sends trading order to the market"""

        plugin_data = {}

        for _plugin in self.plugins:
            log(INFO, f"Execute plugin {_plugin}")
            plugin_data[f"{_plugin}_before"] = _plugin.before_request(
                endpoint, params=params, data=data
            )

        # Check if connection exists
        if not self.trade_protocol.is_connected():
            err = self.trade_protocol.connect(verify_ssl=verify_ssl)

            if err:
                return (None, err)
            
        response, err = self.trade_protocol.send_request(
            method=method,
            endpoint=endpoint,
            data=data,
            ssl=ssl,
            context=self.context,
            user=self.user,
            market=self.market,
            order=market_order,
            **kwargs,
        )

        for _plugin in self.plugins:
            plugin_data[f"{_plugin}_after"] = _plugin.after_request(response)

        return (
            FlexResponse(request_response=response, plugin_data=plugin_data or None),
            err,
        )

    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        ssl: Optional[bool] = True,
        verify_ssl: Optional[bool] = True,
        **kwargs,
    ) -> FlexResponse:
        """Executes all plugins and forwards the request to the protocol API class"""

        plugin_data = {}

        for _plugin in self.plugins:
            log(INFO, f"Execute plugin {_plugin}")

            plugin_data[f"{_plugin}_before"] = _plugin.before_request(
                endpoint, params=params, data=data
            )

        response, err = self.request_protocol.send_request(
            method=method,
            endpoint=endpoint,
            data=data,
            user=self.user,
            market=self.market,
            ssl=ssl,
            verify_ssl=verify_ssl,
            **kwargs,
        )

        for _plugin in self.plugins:
            plugin_data[f"{_plugin}_after"] = _plugin.after_request(response)

        return (
            FlexResponse(request_response=response, plugin_data=plugin_data or None),
            err,
        )

    def add_plugin(self, plugin: BasePlugin):
        """Add a plugin to the list of plugins"""

        for _plugin in self.plugins:
            if type(_plugin) == type(plugin):
                log(
                    WARNING,
                    f"Found already a plugin type {type(plugin)}, plugin"
                    f" {str(plugin)} is not added",
                )
                return
        self.plugins.append(plugin)
        log(INFO, f"Added plugin {plugin}")

    def check_market_responses(self):
        """Check the responses from the market"""

        self.trade_protocol.checkreplies()
        if not self.trade_protocol.callback_responses:
            log(DEBUG, "No responses from the market")
            return None
        return self.trade_protocol.callback_responses
    
    def connect(self) -> None:
        """Connect to the market"""
        if self.user.app_key is None:
            # TODO just a temporary solution
            self.plugins[0].before_request()
        err = self.trade_protocol.connect()
        if err:
            raise err
    
    def disconnect(self) -> None:
        """Disconnect from the market"""
        self.trade_protocol.close_connection()

    def sleep(self, seconds: int) -> None:
        """Sleep for a number of seconds"""
        self.trade_protocol.connection.sleep(seconds)


class MarketMessages:
    """Market messages class to store the market messages, closed deals, ticks"""

    def __init__(self) -> None:
        pass

    @property
    def ticks(self):
        """Get a list of ticks received during the trading session"""
        pass

    def closed_deals(self):
        """Get a list of closed bid and ask deals executed during the trading session"""
        pass

    def _add_market_message(self, message):
        """Add a market message to the list of market messages"""
        pass


#         log(INFO, f"Received message {pformat(msgBody)}")
#         # if 'msgtype' in msgBody.keys():
#         #     if msgBody['msgtype'] == 'cancel':
#         #             log(INFO,"--- Bohoo! My message got cancelled for ", msgBody['reason'])
#         #     if msgBody['msgtype'] == 'tick':
#         #         tickprice = msgBody['last_price']
#         #         log(INFO,"--- Tick ",tickprice)
#         #         if 'sendertimestamp_in_ms' in props.headers.keys():
#         #             log(INFO,f"----- Tick was received in {currTimeMs - props.headers['sendertimestamp_in_ms']} ms")
#         #     if msgBody['msgtype'] == 'bid_closed_order':
#         #         if "closed_order" in msgBody.keys():
#         #             log(INFO,"--- Wohoo! My bid order deal went through for ", msgBody['closed_order']['price'])
#         #     if msgBody['msgtype'] == 'ask_closed_order':
#         #         if "closed_order" in msgBody.keys():
#         #             log(INFO,"--- Wohoo! My ask order deal went through for ", msgBody['closed_order']['price'])
