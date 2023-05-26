from typing import List, Optional
from flxtrd.protocols.base import BaseAPI
from flxtrd.protocols.rest.rest_api import RestAPI
from flxtrd.core.plugins.auth import AuthPlugin
from flxtrd.core.plugins.base import BasePlugin


class FlexAPIClient:
    """Example Client that uses the api and auth plugin"""
    
    def __init__(self, base_url: str, protocol: BaseAPI = RestAPI, plugins: Optional[List[BasePlugin]] = None) -> None:
        self.protocol = protocol(base_url=base_url)
        # By default the Auth Plugin is added
        self.plugins = plugins or [AuthPlugin(app_token="secret")]

    def make_request(self, 
                     method: str,
                     endpoint: str,
                     params: Optional[dict] = None,
                     data: Optional[dict] = None) -> dict:
        """Executes all plugins and forwrds the request to the protocol API class"""

        for _plugin in self.plugins:
            print("Before request")
            print(f"Execute plugin {_plugin} ")
            # _plugin.before_request(endpoint, params=params, data=data)

        response = self.protocol.send_request(method, endpoint, params=params, data=data)

        for _plugin in self.plugins:
            print("After request")
            print(f"Execute plugin {_plugin} ")
            # _plugin.after_request(response)

        return response
    
    def add_plugin(self, plugin: BasePlugin):
        """Add a plugin to the list of plugins"""

        for _plugin in self.plugins:
            if type(_plugin) == type(plugin):
                print(f"Found already a plugin type {type(plugin)}, plugin {str(plugin)} is not added")
                return 
        self.plugins.append(plugin)
        print(f"Added plugin {plugin}")