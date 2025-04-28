# sweph/setupsettings.py
# manage settings for sweph & application (in panelsettings.py)
import swisseph as swe
from user.settings import SWE_FLAG


# class SetupAppSettings:
def get_sweph_flags():
    """configure swisseph flags"""
    flags = 0
    if SWE_FLAG["default flag"]:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if SWE_FLAG["sidereal zodiac"]:
        flags |= swe.FLG_SIDEREAL
    if SWE_FLAG["no nutation"]:
        flags |= swe.FLG_NONUT
    if SWE_FLAG["heliocentric"]:
        flags |= swe.FLG_HELCTR
    if SWE_FLAG["true positions"]:
        flags |= swe.FLG_TRUEPOS
    if SWE_FLAG["topocentric"]:
        flags |= swe.FLG_TOPOCTR
    if SWE_FLAG["equatorial"]:
        flags |= swe.FLG_EQUATORIAL
    if SWE_FLAG["cartesian"]:
        flags |= swe.FLG_XYZ
    if SWE_FLAG["radians"]:
        flags |= swe.FLG_RADIANS
    print(f"getswephflags : {flags}")

    return flags
