from logging import INFO, WARNING
from typing import List, Optional, Tuple

from flxtrd.core.logger import log
from flxtrd.core.plugins.auth import AuthPlugin
from flxtrd.core.plugins.base import BasePlugin
from flxtrd.core.types import APIResponse, FlexError, Market, User
from flxtrd.protocols.ampq import AmpqAPI
from flxtrd.protocols.base import BaseAPI
from flxtrd.protocols.restapi import RestAPI

# userid, applicationKey = validateApplicationToken(authServer=authServer,
#                                                 accessTaken=accessToken,
#                                                 verify_ssl=verify_ssl)


class FlexAPIClient:
    """Example API Client that uses the api and auth plugin

    Params:
        user: User account object
        Market: Market information
        base_url: Base url of the API server
        protocol: Protocol used for communication with the public API of the market
        plugins: List of plugins to use

    """

    def __init__(
        self,
        user: User,
        market: Market,
        base_url: str,
        request_protocol: BaseAPI = RestAPI,
        trade_protocol: AmpqAPI = AmpqAPI,
        plugins: Optional[List[BasePlugin]] = None,
    ) -> None:
        # user account data
        self.user = user
        self.market = market
        self.request_protocol = request_protocol(base_url=base_url)
        self.trade_protocol: AmpqAPI = trade_protocol(
            base_url=base_url, user=user, broker=market.broker
        )

        # By default the Auth Plugin is added
        self.plugins = plugins or [
            AuthPlugin(user=user, authServer=base_url, verify_ssl=False)
        ]
        # Keeps connection alive if the protocol requires it
        self.context = None

    def send_order(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        ssl: Optional[bool] = True,
        verify_ssl: Optional[bool] = True,
        **kwargs,
    ) -> Tuple[APIResponse, FlexError | None]:
        """Sends trading order to the market"""

        plugin_data = {}

        for _plugin in self.plugins:
            log(INFO, f"Execute plugin {_plugin}")
            plugin_data[f"{_plugin!s}_before"] = _plugin.before_request(
                endpoint, params=params, data=data
            )

        # Check is connection is alive
        if not self.trade_protocol.is_connected():
            self.trade_protocol.connect(verify_ssl=verify_ssl)

        if not self.trade_protocol.is_connected():
            raise FlexError("Connection for context is not established")

        response, err = self.trade_protocol.send_request(
            method=method,
            endpoint=endpoint,
            data=data,
            ssl=ssl,
            context=self.context,
            user=self.user,
            market=self.market,
            **kwargs,
        )

        for _plugin in self.plugins:
            plugin_data[f"{_plugin!s}_after"] = _plugin.after_request(response)

        return (
            APIResponse(request_response=response, plugin_data=plugin_data or None),
            err,
        )

    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        ssl: Optional[bool] = False,
        verify_ssl: Optional[bool] = True,
        **kwargs,
    ) -> APIResponse:
        """Executes all plugins and forwards the request to the protocol API class"""

        plugin_data = {}

        for _plugin in self.plugins:
            log(INFO, f"Execute plugin {_plugin}")
            plugin_data[f"{_plugin!s}_before"] = _plugin.before_request(
                endpoint, params=params, data=data
            )

        response, err = self.request_protocol.send_request(
            method=method,
            endpoint=endpoint,
            data=data,
            ssl=ssl,
            user=self.user,
            market=self.market,
            **kwargs,
        )

        for _plugin in self.plugins:
            plugin_data[f"{_plugin!s}_after"] = _plugin.after_request(response)

        return (
            APIResponse(request_response=response, plugin_data=plugin_data or None),
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
