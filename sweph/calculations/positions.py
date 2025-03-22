# ruff: noqa: E402
# ruff: noqa: E701
import swisseph as swe
import datetime

# import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from sweph.swecore import SweCore
from ui.notifymanager import NotifyManager
from user.settings.settings import OBJECTS, SWE_FLAG


class SwePositions:
    """get positions of planets"""

    def __init__(self, get_application=None):
        print("initialising swepositions ...")
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
            else Gtk.Application.get_default()
            # else Gtk.get_application_default()
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
        if SWE_FLAG.get("cartesian"):
            # if SWE_FLAG.get("cartesian", False):
            flags |= swe.FLG_XYZ
        if SWE_FLAG.get("radians"):
            # if SWE_FLAG.get("radians", False):
            flags |= swe.FLG_RADIANS

        return flags

    def _parse_datetime(self, dt_str):
        """parse datetime string"""
        try:
            # expected format : YYYY-MM-DD HH:MM:SS
            dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return {
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": dt.hour,
                "minute": dt.minute,
                "second": dt.second,
            }
        except Exception as e:
            self.notify_user(
                message=f"error parsing datetime : {e}",
                source="swepositions",
                level="error",
            )
            return None

    def _parse_location(self, location_str):
        """parse location string"""
        try:
            # expected format : lat, lon, alt or lat, lon
            parts = location_str.split(",")
            if len(parts) >= 8:
                # latitide
                lat_deg = float(parts[0])
                lat_min = float(parts[1])
                lat_sec = float(parts[2])
                lat_dir = parts[3].strip().lower()
                # longitude
                lon_deg = float(parts[4])
                lon_min = float(parts[5])
                lon_sec = float(parts[6])
                lon_dir = parts[7].strip().lower()
                if len(parts) == 9:
                    alt = float(parts[8])
                # string to decimal degrees
                lat = lat_deg + lat_min / 60 + lat_sec / 3600
                if lat_dir == "s":
                    lat = -lat
                lon = lon_deg + lon_min / 60 + lon_sec / 3600
                if lon_dir == "w":
                    lon = -lon

                return {
                    "lat": lat,
                    "lon": lon,
                    "alt": alt or 0,
                }
            else:
                self.notify_user(
                    message=f"invalid location format : '{location_str}'",
                    source="swepositions",
                    level="error",
                )
                return None

        except Exception as e:
            self.notify_user(
                message=f"error parsing location '{location_str}'\n\tstr({e})",
                source="swepositions",
                level="error",
            )
            return None

            # location = {
            #     "lat": float(parts[0]),
            #     "lon": float(parts[1]),
            # }
            # if len(parts) > 2:
            #     location["alt"] = float(parts[2])
            # else:
            #     location["alt"] = 0
            # return location
        # except Exception as e:
        #     self.notify_user(
        #         message=f"error parsing location : {e}",
        #         source="swepositions",
        #         level="error",
        #     )
        #     return None

    def swe_events_data(self):
        """prepare event data for swe calculations"""
        self.notify_user(
            message="preparing swisseph data OLO", level="debug", source="swepositions"
        )
        events_data = self.swe_core.swe_ready_data()
        if not events_data:
            self.notify_user(
                message="no events data", level="error", source="swepositions"
            )
            return {}

        results = {}
        for event_name, event_details in events_data.items():
            # skip empty events
            if not event_name or not event_details or not event_details[3]:
                continue
            try:
                # parse datetime to julian day
                dt_parts = self._parse_datetime(event_details[3])
                if not dt_parts:
                    continue
                jd_ut = swe.julday_ut(
                    dt_parts["year"],
                    dt_parts["month"],
                    dt_parts["day"],
                    dt_parts["hour"]
                    + dt_parts["minute"] / 60
                    + dt_parts["second"] / 3600,
                )
                # parse location
                location = self._parse_location(event_details[2])
                if location:
                    results[event_name] = self.calculate(
                        jd_ut,
                        lat=location["lat"],
                        lon=location["lon"],
                        alt=location.get("alt", 0),
                    )
                else:
                    results[event_name] = self.calculate(jd_ut)

                self.notify_user(
                    message=f"calculated {event_name}",
                    level="debug",
                    source="swepositions",
                )
            except Exception as e:
                self.notify_user(
                    message=f"error processing {event_name}\n\tstr({e})",
                    source="swepositions",
                    level="error",
                )
        # present results
        if results:
            self.notify_user(
                message=f"results : {list(results.keys())}",
                # message=f"results : {results}",
                source="swepositions",
                level="success",
            )
        return results

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
                    f"error calculating {planet_code} : str({e})",
                    source="swepositions",
                    level="error",
                )
        return results
