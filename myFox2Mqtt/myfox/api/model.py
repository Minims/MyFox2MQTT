"""Models Definition"""

from enum import Enum
from typing import Any, Dict


class Site:
    """Site Object"""

    __slots__ = (
        "siteId",
        "label",
        "brand",
        "timezone",
        "AXA",
        "cameraCount",
        "gateCount",
        "shutterCount",
        "socketCount",
        "moduleCount",
        "heaterCount",
        "scenarioCount",
        "deviceTemperatureCount",
        "deviceStateCount",
        "deviceLightCount",
        "deviceDetectorCount",
        "arcsoftToken",
        "buzzSiteId",
    )

    def __init__(
        self,
        siteId: int,
        label: str,
        brand: str,
        timezone: str,
        AXA: str,
        cameraCount: int,
        gateCount: int,
        shutterCount: int,
        socketCount: int,
        moduleCount: int,
        heaterCount: int,
        scenarioCount: int,
        deviceTemperatureCount: int,
        deviceStateCount: int,
        deviceLightCount: int,
        deviceDetectorCount: int,
        arcsoftToken: str,
        buzzSiteId: int,
        **_: Any,
    ):
        self.siteId = siteId  # pylint: disable=invalid-name
        self.label = label
        self.brand = brand
        self.timezone = timezone
        self.AXA = AXA
        self.cameraCount = cameraCount
        self.gateCount = gateCount
        self.shutterCount = shutterCount
        self.socketCount = socketCount
        self.moduleCount = moduleCount
        self.heaterCount = heaterCount
        self.scenarioCount = scenarioCount
        self.deviceTemperatureCount = deviceTemperatureCount
        self.deviceStateCount = deviceStateCount
        self.deviceLightCount = deviceLightCount
        self.deviceDetectorCount = deviceDetectorCount
        self.arcsoftToken = arcsoftToken
        self.buzzSiteId = buzzSiteId


class Device:
    """Device Object"""

    __slots__ = (
        "id",
        "site_id",
        "box_id",
        "label",
        "version",
        "device_definition",
        "status",
        "diagnosis",
        "settings",
        "update_available",
    )

    def __init__(
        self,
        device_id: str,
        site_id: str,
        box_id: str,
        label: str,
        version: str,
        device_definition: Dict,
        status: Dict,
        diagnosis: Dict,
        settings: Dict,
        update_available: str,
        **_: Any,
    ):
        self.id = device_id  # pylint: disable=invalid-name
        self.site_id = site_id
        self.box_id = box_id
        self.label = label
        self.version = version
        self.device_definition = device_definition
        self.status = status
        self.diagnosis = diagnosis
        self.settings = settings
        self.update_available = update_available


class AvailableStatus(Enum):
    """List of Allowed Security Level
    Args:
        Enum (str): Security Level
    """

    DISARMED = 1
    ARMED = 2
    PARTIAL = 3


class Status:
    """Alarm Status"""

    def __init__(self, security_level: AvailableStatus):
        self.security_level = security_level


class User:
    """User Object"""

    __slots__ = (
        "id",
        "display_name",
        "display_my_presence",
        "present",
        "activated",
        "geoFence",
    )

    def __init__(
        self,
        user_id: str,
        display_name: str,
        display_my_presence: str,
        present: str,
        activated: str,
        geo_fence: Dict,
        **_: Any,
    ):
        self.id = user_id  # pylint: disable=invalid-name
        self.display_name = display_name
        self.display_my_presence = display_my_presence
        self.present = present
        self.activated = activated
        self.geoFence = geo_fence
