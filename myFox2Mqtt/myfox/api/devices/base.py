"""Device Managment"""

from typing import Union

from myfox.api.model import Device, Site
from myfox.api import MyFoxApi


class MyFoxDevice:
    """MyFox Device"""

    __slots__ = "site", "device", "api"

    def __init__(self, site: Site, device: Device, api: MyFoxApi):
        self.site = site
        self.device = device
        self.api = api

    def refresh_state(self) -> None:
        """Refresh State"""
        self.device = self.api.get_device(site_id=self.site.id, device_id=self.device.device_id)

    def get_status(self, status_name: str) -> Union[str, int, float]:
        """Get a Status for the current device.

        Args:
            status_name (str): Name of status

        Returns:
            Union[str, int, float]: Status value
        """
        if not status_name:
            return None
        return self.device.status.get(status_name)

    def get_setting(self, setting_name: str) -> Union[str, int, float]:
        """Get a Setting for the current device.

        Args:
            setting_name (str): Name of setting

        Returns:
            Union[str, int, float]: Status value
        """
        if not setting_name:
            return None
        return self.device.settings.get(setting_name)
