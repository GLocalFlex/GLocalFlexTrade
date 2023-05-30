from typing import List, Optional, Tuple
from flxtrd.protocols.base import BaseAPI
from flxtrd.protocols.restapi import RestAPI
from flxtrd.core.plugins.auth import AuthPlugin, AuthResponse
from flxtrd.core.plugins.base import BasePlugin
from flxtrd.core.types import User, APIResponse


class FlexAPIClient:
    """Example API Client that uses the api and auth plugin
    
    Params:
        user: User object
        base_url: Base url of the API
        protocol: Protocol to use for communication with the public API
        plugins: List of plugins to use

    """
    
    def __init__(self, user: User,  base_url: str, protocol: BaseAPI = RestAPI, plugins: Optional[List[BasePlugin]] = None) -> None:
        self.protocol = protocol(base_url=base_url)
        # By default the Auth Plugin is added
        self.plugins = plugins or [AuthPlugin(user=user,
                                              authServer=base_url)]

    def make_request(self, 
                     method: str,
                     endpoint: str,
                     params: Optional[dict] = None,
                     ssl: Optional[bool] = False,
                     data: Optional[dict] = None,
                     user: User = None) ->  APIResponse:
        """Executes all plugins and forwards the request to the protocol API class"""

        plugin_data = {}

        for _plugin in self.plugins:
            print(f"Execute plugin {_plugin}")
            plugin_data[f"{str(_plugin)}_before"] =  _plugin.before_request(endpoint, params=params, data=data)

        
        response, err= self.protocol.send_request(method,
                                              endpoint,
                                              params=params,
                                              data=data,
                                              ssl=ssl)

        for _plugin in self.plugins:
            plugin_data[f"{str(_plugin)}_after"] = _plugin.after_request(response)

        return APIResponse(request_response=response, plugin_data=plugin_data or None) , err

    
    def add_plugin(self, plugin: BasePlugin):
        """Add a plugin to the list of plugins"""

        for _plugin in self.plugins:
            if type(_plugin) == type(plugin):
                print(f"Found already a plugin type {type(plugin)}, plugin {str(plugin)} is not added")
                return 
        self.plugins.append(plugin)
        print(f"Added plugin {plugin}")