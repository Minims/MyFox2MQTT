"""Devices Categories"""
from aenum import Enum, unique


@unique
class Category(Enum):
    """List of Known Devices"""

    LINK = "Link"
    CENTRAL = "Myfox HC2"
    INDOOR_SIREN = "Sirène d'intérieur"
    OUTDOOR_SIREN = "Sirène d'extérieur"
    MOTION = "Détecteur de mouvement"
    KEYBOARD = "Clavier"
    SMOKE_DETECTOR = "Détecteur de fumée"
    INTELLITAG = "IntelliTAG"
    TAG = "Capteur TAG"
    KEY_FOB = "Télécommande 4 boutons"

    @classmethod
    def _missing_name_(cls, name):
        for member in cls:
            if member.name.lower() == name.lower():
                return member
