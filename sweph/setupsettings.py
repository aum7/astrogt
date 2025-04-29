# sweph/setupsettings.py
# manage settings for sweph & application (in panelsettings.py)
# flag details in user/settings.py
import swisseph as swe
from user.settings import SWE_FLAG


def get_sweph_flags_int():
    """get initial sweph flags"""
    flags = 0
    if SWE_FLAG["sidereal zodiac"][0]:
        flags |= swe.FLG_SIDEREAL
    if SWE_FLAG["true positions"][0]:
        flags |= swe.FLG_TRUEPOS
    if SWE_FLAG["topocentric"][0]:
        flags |= swe.FLG_TOPOCTR
    if SWE_FLAG["heliocentric"][0]:
        flags |= swe.FLG_HELCTR
    if SWE_FLAG["default flag"][0]:
        flags |= swe.FLG_SWIEPH | swe.FLG_SPEED
    if SWE_FLAG["no nutation"][0]:
        flags |= swe.FLG_NONUT
    if SWE_FLAG["no abberation"][0]:
        flags |= swe.FLG_NOABERR
    if SWE_FLAG["no deflection"][0]:
        flags |= swe.FLG_NOGDEFL
    if SWE_FLAG["equatorial"][0]:
        flags |= swe.FLG_EQUATORIAL
    if SWE_FLAG["cartesian"][0]:
        flags |= swe.FLG_XYZ
    if SWE_FLAG["radians"][0]:
        flags |= swe.FLG_RADIANS
    print(f"setupsettings : getswephflags : {flags}")

    return flags
