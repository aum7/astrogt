# ruff: noqa: E402
# ruff: noqa: E701
import swisseph as swe

# import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from swe.swecore import SweCore
from ui.notifymanager import NotifyManager
from user.settings import OBJECTS, SWE_FLAG


class SwePositions:
    """get positions of planets"""

    def __init__(self, ephe_path=None, get_application=None):
        self.get_application = get_application
        # configure flags
        self.swe_flag = self._get_swe_flags()

        self.swe_core = SweCore()
        self.notify_manager = NotifyManager()

        self.notify_user(
            f"sweposition : {self.swe_core.event_one_name}",
            source="swepositions",
            level="debug",
        )
        self.swe_events_data()

    def notify_user(self, message, **kwargs):
        app = (
            self.get_application()
            if self.get_application
            else Gtk.get_application_default()
        )
        if app and hasattr(app, "notify_manager"):
            app.notify_manager.notify(message=message, **kwargs)
        else:
            print(f"eventdata : {message}")

    def _get_swe_flags(self):
        """configure swisseph flags"""
        flags = SWE_FLAG["swe_flag_default"]

        if SWE_FLAG["sidereal_zodiac"]:
            flags |= swe.FLG_SIDEREAL
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

    def swe_events_data(self):
        """prepare event data for swe calculations"""
        self.notify_user(message="preparing swisseph data OLO")
        # dt = ""
        # if len(dt) < 5:
        #     return {"error": "invalid date time format"}

    def calculate(self, jd_ut, lat=None, lon=None, alt=None):
        if SWE_FLAG["topocentric"] and lat and lon:
            swe.set_topo(lat, lon, alt)
        results = {}
        for planet_code, (swe_id, names) in OBJECTS.items():
            try:
                result = swe.calc_ut(jd_ut, swe_id, self.swe_flag)
                results[planet_code] = {
                    "longitude": result[0],
                    "latitude": result[1],
                    "distance": result[2],
                    "speed_long": result[3],
                    "speed_lat": result[4],
                    "speed_distance": result[5],
                    "name": names[0],
                }
            except Exception as e:
                self.notify_user(
                    f"error calculating {planet_code} : {e}",
                    source="swepositions",
                    level="error",
                )
        return results
