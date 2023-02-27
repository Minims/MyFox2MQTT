"""MyFox Api"""
import logging
import json
from json import JSONDecodeError
from typing import Any, Dict, List, Optional

from myfox.api.devices.category import Category
from myfox.api.model import AvailableStatus, Device, Site, User
from myfox.sso import MyFoxSso
from oauthlib.oauth2 import TokenExpiredError
from requests import Response

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.myfox.me"

ACTION_LIST = [
    "shutter_open",
    "shutter_close",
    "autoprotection_pause",
    "battery_changed",
    "change_video_backend",
    "checkin",
    "checkout",
    "firmware_update_start",
    "range_test_start",
    "range_test_stop",
    "garage_close",
    "garage_learn",
    "garage_open",
    "gate_close",
    "gate_learn",
    "gate_open",
    "light_learn",
    "light_off",
    "light_on",
    "mounted",
    "prepare_push_to_talk",
    "reboot",
    "halt",
    "rolling_shutter_down",
    "rolling_shutter_learn",
    "rolling_shutter_up",
    "measure_ambient_light",
    "stream_start",
    "stream_stop",
    "test_extend",
    "test_stop",
    "siren_3_sec",
    "test_start",
    "test_mfa",
    "sound_test",
]


class MyFoxApi:
    """MyFox Api Class"""

    def __init__(self, sso: MyFoxSso):
        self.sso = sso

    def _request(self, method: str, path: str, **kwargs: Any) -> Response:
        """Make a request.

        We don't use the built-in token refresh mechanism of OAuth2 session because
        we want to allow overriding the token refresh logic.

        Args:
            method (str): HTTP Methid
            path (str): Path to request

        Returns:
            Response: requests Response object
        """

        url = f"{BASE_URL}{path}"
        try:
            return getattr(self.sso._oauth, method)(url, **kwargs)  # pylint: disable=protected-access
        except TokenExpiredError:
            self.sso._oauth.token = self.sso.refresh_tokens()  # pylint: disable=protected-access

            return getattr(self.sso._oauth, method)(url, **kwargs)  # pylint: disable=protected-access

    def get(self, path: str) -> Response:
        """Fetch an URL from the MyFox API.

        Args:
            path (str): Path to request

        Returns:
            Response: requests Response object
        """
        return self._request("get", path)

    def post(self, path: str, *, json: Dict[str, Any]) -> Response:
        """Post data to the MyFox API.

        Args:
            path (str): Path to request
            json (Dict[str, Any]): Data in json format

        Returns:
            Response: requests Response object
        """
        return self._request("post", path, json=json)

    def put(self, path: str, *, json: Dict[str, Any]) -> Response:
        """Put data to the MyFox API.

        Args:
            path (str): Path to request
            json (Dict[str, Any]): Data in json format

        Returns:
            Response: requests Response object
        """
        LOGGER.info(json)
        return self._request("put", path, json=json)

    def get_sites(self) -> List[Site]:
        """Get All Sites

        Returns:
            List[Site]: List of Site object
        """
        response = self.get("/v2/client/site/items")
        response.raise_for_status()
        LOGGER.info(f"Sites: {response.json()}")
        return [Site(**s) for s in response.json().get("payload").get("items")]

    def get_site(self, site_id: str) -> Dict:
        """Get Site

        Args:
            site_id (str): Site ID


        Returns:
            Site: Site object
        """
        response = self.get(f"/v2/site/{site_id}")
        response.raise_for_status()
        LOGGER.info(f"Site: {response.json()}")
        return response.json()

    def get_site_status(self, site_id: str) -> Dict:
        """Get Site

        Args:
            site_id (str): Site ID


        Returns:
            Site: Site object
        """
        response = self.get(f"/v2/site/{site_id}/security")
        response.raise_for_status()
        LOGGER.info(f"Site Status: {response.json()}")
        return response.json()

    def update_security_level(self, site_id: str, security_level: AvailableStatus) -> Dict:
        """Set Alarm Security Level

        Args:
            site_id (str): Site ID
            security_level (AvailableStatus): Security Level
        Returns:
            Dict: requests Response object
        """
        response = self.post(f"/v2/site/{site_id}/security/set/{security_level.lower()}", json={})
        response.raise_for_status()
        return response.json()

    def stop_alarm(self, site_id: str) -> Dict:
        """Stop Current Alarm

        Args:
            site_id (str): Site ID
        Returns:
            Dict: requests Response object
        """
        response = self.put(f"/v2/site/{site_id}/alarm/stop", json={})
        response.raise_for_status()
        return response.json()

    def trigger_alarm(self, site_id: str, mode: str) -> Dict:
        """Trigger Alarm

        Args:
            site_id (str): Site ID
            mode (str): Mode (silent, alarm)
        Returns:
            Dict: requests Response object
        """
        if mode not in ["silent", "alarm"]:
            raise ValueError("Mode must be 'silent' or 'alarm'")
        payload = {"type": mode}
        response = self.post(f"/v2/site/{site_id}/panic", json=payload)
        response.raise_for_status()
        return response.json()

    def action_device(
        self,
        site_id: str,
        device_id: str,
        action: str,
    ) -> Dict:
        """Make an action on a Device

        Args:
            site_id (str): Site ID
            device_id (str): Device ID
            action (str): Action

        Returns:
            str: Task ID
        """
        if action not in ACTION_LIST:
            raise ValueError(f"Unknown action {action}")

        response = self.post(
            f"/v2/site/{site_id}/device/{device_id}/action",
            json={"action": action},
        )
        response.raise_for_status()
        return response.json()

    def update_device(
        self,
        site_id: str,
        device_id: str,
        device_label: str,
        settings: Dict,
    ) -> Dict:
        """Update Device Settings

        Args:
            site_id (str): Site ID
            device_id (str): Device ID
            device_label (str): Device Label
            settings (Dict): Settings (as return by get_device)

        Returns:
            str: Task ID
        """
        if settings is None or device_label is None:
            raise ValueError("Missing settings and/or device_label")

        # Clean Settings Dict
        settings.pop("object")

        payload = {"settings": settings, "label": device_label}
        response = self.put(f"/v2/site/{site_id}/device/{device_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def camera_snapshot(self, site_id: str, device_id: str):
        """Get Camera Snapshot

        Args:
            site_id (str): Site ID
            device_id (str): Site ID

        Returns:
            Response: Response Image
        """
        response = self.post(
            f"/video/site/{site_id}/device/{device_id}/snapshot",
            json={"refresh": 10},
        )
        response.raise_for_status()
        if response.status_code == 200:
            return response

    def camera_refresh_snapshot(self, site_id: str, device_id: str) -> Device:
        """Get Camera Snapshot

        Args:
            site_id (str): Site ID
            device_id (str): Site ID

        Returns:
            Task: MyFox Task
        """
        response = self.post(
            f"/video/site/{site_id}/device/{device_id}/refresh-snapshot",
            json={},
        )
        response.raise_for_status()
        return response.json()

    def get_devices(self, site_id: str, category: Optional[Category] = None) -> List[Device]:
        """List Devices from a Site ID

        Args:
            site_id (Optional[str], optional): Site ID. Defaults to None.
            category (Optional[Category], optional): [description]. Defaults to None.

        Returns:
            List[Device]: List of Device object
        """
        devices = []  # type: List[Device]
        response = self.get(f"/v2/site/{site_id}/device")
        try:
            content = response.json()
        except JSONDecodeError:
            response.raise_for_status()
        LOGGER.info(f"Devices: {response.json()}")
        devices += [
            Device(**d)
            for d in content.get("payload").get("items")
            if category is None
            or category.value.lower() in Device(**d).device_definition.get("device_definition_label").lower()
        ]
        return devices

    def get_device(self, site_id: str, device_id: str) -> Device:
        """Get Device details

        Args:
            site_id (str): Site ID
            device_id (str): Site ID

        Returns:
            Device: Device object
        """
        response = self.get(f"/v2/site/{site_id}/device/{device_id}")
        response.raise_for_status()
        LOGGER.info(f"Device: {response.json()}")
        return Device(**response.json())

    def get_users(self, site_id: str) -> List[User]:
        """List Users from a Site ID

        Args:
            site_id[str]: Site ID. Defaults to None.

        Returns:
            List[User]: List of User object
        """
        response = self.get(f"/v2/site/{site_id}/user")
        response.raise_for_status()
        return [User(**s) for s in response.json().get("items")]

    def get_user(self, site_id: str, user_id: str) -> User:
        """Get User details

        Args:
            site_id (str): Site ID
            user_id (str): Site ID

        Returns:
            User: User object
        """
        response = self.get(f"/v2/site/{site_id}/user/{user_id}")
        response.raise_for_status()
        return User(**response.json())

    def action_user(
        self,
        site_id: str,
        user_id: str,
        action: str,
    ) -> Dict:
        """Make an action on a User

        Args:
            site_id (str): Site ID
            user_id (str): User ID
            action (str): Action

        Returns:
            str: Task ID
        """
        if action not in ACTION_LIST:
            raise ValueError(f"Unknown action {action}")

        response = self.post(
            f"/v2/site/{site_id}/user/{user_id}/action",
            json={"action": action},
        )
        response.raise_for_status()
        return response.json()

    def get_scenarios_core(
        self,
        site_id: str,
    ):
        """Get Scenarios Core

        Args:
            site_id (str): Site ID

        Returns:
            ??
        """
        response = self.get(f"/v2/site/{site_id}/scenario-core")
        response.raise_for_status()
        return response.json()

    def get_scenarios(
        self,
        site_id: str,
    ):
        """Get Scenarios

        Args:
            site_id (str): Site ID

        Returns:
            ??
        """
        response = self.get(f"/v2/site/{site_id}/scenario/items")
        response.raise_for_status()
        LOGGER.info(f"Scenarios: {response.json()}")
        return response.json()

    def get_devices_temperature(self, site_id: str, category: Optional[Category] = None):
        """List Devices from a Site ID

        Args:
            site_id (Optional[str], optional): Site ID. Defaults to None.
            category (Optional[Category], optional): [description]. Defaults to None.

        Returns:
        """
        response = self.get(f"/v2/site/{site_id}/device/data/temperature/items")
        try:
            content = response.json()
        except JSONDecodeError:
            response.raise_for_status()
        LOGGER.info(f"Devices Temperature: {response.json()}")
        return content.get("payload").get("items")

    def get_device_temperature(self, site_id: str, device_id: str):
        """Get Device

        Args:
            site_id (str): Site ID
            device_id (str): Site ID

        Returns:
            Device: Device object
        """
        response = self.get(f"/v2/site/{site_id}/device/{device_id}/data/temperature/")
        response.raise_for_status()
        LOGGER.info(f"Device: {response.json()}")
        return response.json()

    def get_devices_state(self, site_id: str, category: Optional[Category] = None):
        """List Devices from a Site ID

        Args:
            site_id (Optional[str], optional): Site ID. Defaults to None.
            category (Optional[Category], optional): [description]. Defaults to None.

        Returns:
            List[Device]: List of Device object
        """
        devices = []  # type: List[Device]
        response = self.get(f"/v2/site/{site_id}/device/data/state/items")
        try:
            content = response.json()
        except JSONDecodeError:
            response.raise_for_status()
        LOGGER.info(f"Devices State: {response.json()}")
        return content.get("payload").get("items")

    def get_device_state(self, site_id: str, device_id: str):
        """Get Device

        Args:
            site_id (str): Site ID
            device_id (str): Site ID

        Returns:
            Device: Device object
        """
        response = self.get(f"/v2/site/{site_id}/device/{device_id}/data/state/")
        response.raise_for_status()
        LOGGER.info(f"Device: {response.json()}")
        return response.json()

    def get_devices_light(self, site_id: str, category: Optional[Category] = None):
        """List Devices from a Site ID

        Args:
            site_id (Optional[str], optional): Site ID. Defaults to None.
            category (Optional[Category], optional): [description]. Defaults to None.

        Returns:
            List[Device]: List of Device object
        """
        response = self.get(f"/v2/site/{site_id}/device/data/light/items")
        try:
            content = response.json()
        except JSONDecodeError:
            response.raise_for_status()
        LOGGER.info(f"Devices Light: {response.json()}")
        return content.get("payload").get("items")

    def get_device_light(self, site_id: str, device_id: str):
        """Get Device

        Args:
            site_id (str): Site ID
            device_id (str): Site ID

        Returns:
            Device: Device object
        """
        response = self.get(f"/v2/site/{site_id}/device/{device_id}/data/light/")
        response.raise_for_status()
        LOGGER.info(f"Device: {response.json()}")
        return response.json()

    def get_devices_other(self, site_id: str, category: Optional[Category] = None):
        """List Devices from a Site ID

        Args:
            site_id (Optional[str], optional): Site ID. Defaults to None.
            category (Optional[Category], optional): [description]. Defaults to None.

        Returns:
            List[Device]: List of Device object
        """
        response = self.get(f"/v2/site/{site_id}/device/data/other/items")
        try:
            content = response.json()
        except JSONDecodeError:
            response.raise_for_status()
        LOGGER.info(f"Devices Other: {response.json()}")
        return content.get("payload").get("items")

    def get_devices_camera(self, site_id: str, category: Optional[Category] = None):
        """List Devices from a Site ID

        Args:
            site_id (Optional[str], optional): Site ID. Defaults to None.
            category (Optional[Category], optional): [description]. Defaults to None.

        Returns:
            List[Device]: List of Device object
        """
        devices = []  # type: List[Device]
        response = self.get(f"/v2/site/{site_id}/device/camera/items")
        try:
            content = response.json()
        except JSONDecodeError:
            response.raise_for_status()
        LOGGER.info(f"Devices Camera: {response.json()}")
        return content.get("payload").get("items")
