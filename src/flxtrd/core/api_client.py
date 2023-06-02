from logging import INFO, WARNING
from typing import List, Optional

from flxtrd.core.logger import log
from flxtrd.core.plugins.auth import AuthPlugin
from flxtrd.core.plugins.base import BasePlugin
from flxtrd.core.types import APIResponse, FlexError, Market, User
from flxtrd.protocols.ampq import AmpqAPI, AmpqContext
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
        protocol: BaseAPI = RestAPI,
        plugins: Optional[List[BasePlugin]] = None,
    ) -> None:
        # user account data
        self.user = user
        self.market = market
        self.protocol = protocol(base_url=base_url)

        # By default the Auth Plugin is added
        self.plugins = plugins or [
            AuthPlugin(user=user, authServer=base_url, verify_ssl=False)
        ]
        # Keeps connection alive if the protocol requires it
        self.context = None

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
        """Executes all plugins and forwards the request to the protocol API class
        """

        # Check is connection is alive
        create_context = False
        if self.context is None:
            create_context = True
        elif not self.context.is_connected():
            create_context = True

        plugin_data = {}

        for _plugin in self.plugins:
            log(INFO, f"Execute plugin {_plugin}")
            plugin_data[f"{_plugin!s}_before"] = _plugin.before_request(
                endpoint, params=params, data=data
            )

        if create_context:
            self.context = self._require_api_context(
                protocol=self.protocol,
                verify_ssl=verify_ssl,
                user=self.user,
                market=self.market,
            )
            # check if context was created since it is not necessary for all protocols
            # if created connect to the broker
            if self.context is not None:
                self.context.connect()

        if self.context is not None and not self.context.is_connected():
            raise FlexError("Connection for context is not established")

        response, err = self.protocol.send_request(
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
            APIResponse(
                request_response=response, plugin_data=plugin_data or None
            ),
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

    @staticmethod
    def _require_api_context(
        user: User,
        market: Market,
        protocol: BaseAPI,
        verify_ssl: bool = True,
        **kwargs,
    ):
        """Creates a connection context which is specific for every protocol.
        Rest API do no require any context the function will return None as default
        """
        if isinstance(protocol, AmpqAPI):
            return AmpqContext(
                user=user, broker=market.broker, verify_ssl=verify_ssl
            )
        else:
            return None
