# prepare settings for application, from settings.py
import swisseph as swe
from swisseph import contrib as swh
from user.settings.settings import SWE_FLAG  # ,OBJECTS


class SetupSettings:
    def _get_swe_flags(self):
        """configure swisseph flags"""
        flags = 0
        SWE_FLAG["swe_flag_default"]
        if SWE_FLAG["sidereal_zodiac"]:
            flags |= swe.FLG_SIDEREAL
            # flags |= swe.FLG_SIDEREAL
        if SWE_FLAG["nutation"]:
            flags |= swe.FLG_NONUT
        if SWE_FLAG["heliocentric"]:
            flags |= swe.FLG_HELCTR
        if SWE_FLAG["true_positions"]:
            flags |= swe.FLG_TRUEPOS
        if SWE_FLAG["topocentric"]:
            flags |= swe.FLG_TOPOCTR
        if SWE_FLAG["equatorial"]:
            flags |= swe.FLG_EQUATORIAL
        if SWE_FLAG["cartesian"]:
            flags |= swe.FLG_XYZ
        if SWE_FLAG["radians"]:
            flags |= swe.FLG_RADIANS

        return flags
