"""Devices Categories"""
from aenum import Enum, unique


@unique
class Category(Enum):
    """List of Known Devices"""

    LINK = "Link"
    MYFOX_CAMERA = "Myfox security camera"
    INDOOR_SIREN = "Myfox Security Siren"
    OUTDOOR_SIREN = "Myfox Security Outdoor Siren"
    MOTION = "Myfox Security Infrared Sensor"
    EXTENDER = "Myfox Security Extender"

    @classmethod
    def _missing_name_(cls, name):
        for member in cls:
            if member.name.lower() == name.lower():
                return member
