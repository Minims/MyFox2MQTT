"""Models Definition"""

from enum import Enum
from typing import Any, Dict, Optional


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
        "device_id",
        "label",
        "device_definition",
        "settings",
        "created_at",
        "zone_family",
    )

    def __init__(
        self,
        device_id: int,
        label: str,
        device_definition: Dict,
        settings: Dict,
        created_at: str,
        zone_family: Optional[str] = "",
        **_: Any,
    ):
        self.device_id = device_id
        self.label = label
        self.device_definition = device_definition
        self.settings = settings
        self.created_at = created_at
        self.zone_family = zone_family


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
