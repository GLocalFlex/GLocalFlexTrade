from flxtrd.core.plugins.base import BasePlugin
import json


class ListDevices(BasePlugin):

    def __init__(self):
        super().__init__()

    def before_request(self, *args,**kwargs) -> None:
        return None

    def after_request(self, response: dict) -> None | dict:
        """Retrieves the location from the user which contains registerd devices and returns id and device name"""
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None
        try:
            user_data = response.json()
        except Exception as e:
            raise(e)

        devices = {}
        if user_data.get("locations", None):
            locations = user_data["locations"]
            print(f"User has {len(locations)} devices in user account")
            for location in locations:
                # print(f"Device id: {location['_id']} \t Device name: {location['name']}")
                devices[location['_id']] = location['name']
            return devices
        else:
            return None

    def __str__(self):
        return "ListDevices"
