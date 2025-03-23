# ruff: noqa: E402
import os
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject  # type: ignore
from typing import Optional, Union, Dict
from user.settings.settings import SWE_FLAG  # ,OBJECTS
from datetime import datetime
from ui.notifymanager import NotifyManager
from ui.signalmanager import SignalManager


class SweCore(GObject.Object):
    """note : swisseph calculations need be closed at the end of computations"""

    # signals
    __gsignals__ = {
        "event-one-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        "event-two-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
    }

    # swiss ephemeris path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ephe_path = os.path.join(current_dir, "ephe")
    swe.set_ephe_path(ephe_path)

    def __init__(self, get_application=None):
        super().__init__()
        self._get_application = get_application or Gtk.Application.get_default()
        self.notify_manager = NotifyManager(self._get_application)
        self.signal_manager = SignalManager(self._get_application)
        # event one
        self.event_one_name = ""
        self.event_one_country = ""
        self.event_one_city = ""
        # need be parsed
        self.event_one_location = ""
        self.event_one_date_time = ""
        # event two
        self.event_two_name = ""
        self.event_two_country = ""
        self.event_two_city = ""
        # need be parsed
        self.event_two_location = ""
        self.event_two_date_time = ""
        # close swe after initialisation
        swe.close()

    def notify_user(self, message, level="info", **kwargs):
        """show app notification"""
        try:
            if self._get_application and hasattr(
                self._get_application, "notify_manager"
            ):
                if level == "info":
                    self._get_application.notify_manager.info(message=message, **kwargs)
                elif level == "warning":
                    self._get_application.notify_manager.warning(
                        message=message, **kwargs
                    )
                elif level == "error":
                    self._get_application.notify_manager.error(
                        message=message, **kwargs
                    )
                elif level == "success":
                    self._get_application.notify_manager.success(
                        message=message, **kwargs
                    )
                elif level == "debug":
                    self._get_application.notify_manager.debug(
                        message=message, **kwargs
                    )
                else:
                    print(f"unknown level : {level}")
        except Exception as e:
            print(f"swecore : notification failed\n{e}")

    def get_events_data(self, event_one=None, event_two=None):
        """process event data using swisseph"""

        def has_data_changed(event_data, event_type):
            changed = False
            if event_type == "event_one":
                if (
                    event_data["name"] != self.event_one_name
                    or event_data["date_time"] != self.event_one_date_time
                    or event_data["country"] != self.event_one_country
                    or event_data["city"] != self.event_one_city
                    or event_data["location"] != self.event_one_location
                ):
                    changed = True
            elif event_type == "event_two":
                if (
                    event_data["name"] != self.event_two_name
                    or event_data["date_time"] != self.event_two_date_time
                    or event_data["country"] != self.event_two_country
                    or event_data["city"] != self.event_two_city
                    or event_data["location"] != self.event_two_location
                ):
                    changed = True
            return changed

        if event_one:
            print("processing event one")
            if (
                not event_one["name"]
                or not event_one["date_time"]
                or not event_one["country"]
                or not event_one["city"]
                or not event_one["location"]
            ):
                self.notify_user(
                    message="event one : data missing",
                    source="swecore",
                )
                return {}
            # check if data has changed
            if has_data_changed(event_one, "event_one"):
                # self.notify_user(
                #     message="event one : data changed",
                #     source="swecore",
                # )
                # data received
                self.event_one_name = event_one["name"]
                self.event_one_date_time = event_one["date_time"]
                self.event_one_country = event_one["country"]
                self.event_one_city = event_one["city"]
                self.event_one_location = event_one["location"]
                # process data
                self.swe_ready_data()
                # emit signal for positions, houses, aspects etc
                self.emit("event-one-changed", self)
                print("swecore : emitted event-one-changed")

                # self.notify_user(
                #     message=f"event one data received :"
                #     f"\n\tname : {event_one['name']}"
                #     f"\n\tdatetime : {event_one['date_time']}"
                #     f"\n\tcountry : {event_one['country']}"
                #     f"\n\tcity : {event_one['city']}"
                #     f"\n\tlocation : {event_one['location']}",
                #     source="swecore",
                # )
            else:
                self.notify_user(
                    message="event one : data NOT changed",
                    source="swecore",
                )
        if event_two:
            print("processing event two")
            # for event two only datetime is mandatory
            if not event_two["date_time"]:
                self.notify_user(
                    message="event two : datetime missing : setting to event one datetime",
                    source="swecore",
                    timeout=1,
                )
                event_two["date_time"] = self.event_one_date_time
                # not good solution
                # event_two["date_time"] = datetime.now(timezone.utc).strftime(
                #     "%Y-%m-%d %H:%M:%S"
                # )
            if not event_two["name"]:
                event_two["name"] = self.event_one_name
            # if location not provided, use event one location
            if not event_two["country"]:
                event_two["country"] = self.event_one_country
            if not event_two["city"]:
                event_two["city"] = self.event_one_city
            if not event_two["location"]:
                event_two["location"] = self.event_one_location
            # check if data has changed
            if has_data_changed(event_two, "event_two"):
                # self.notify_user(
                #     message="event two : data changed ...",
                #     source="swecore",
                # )
                # data received
                self.event_two_name = event_two["name"]
                self.event_two_date_time = event_two["date_time"]
                self.event_two_country = event_two["country"]
                self.event_two_city = event_two["city"]
                self.event_two_location = event_two["location"]
                # process data
                self.swe_ready_data()
                # emit signal for positions, houses, aspects etc
                self.emit("event-two-changed", self)
                print("swecore : emitted event-two-changed")

                # self.notify_user(
                #     message=f"event two data received :"
                #     f"\n\tname : {event_two['name']}"
                #     f"\n\tdatetime : {event_two['date_time']}"
                #     f"\n\tcountry : {event_two['country']}"
                #     f"\n\tcity : {event_two['city']}"
                #     f"\n\tlocation : {event_two['location']}",
                #     source="swecore",
                # )
            else:
                self.notify_user(
                    message="event two : data NOT changed",
                    source="swecore",
                )

    def swe_ready_data(self):
        """prepare event data for swe calculations"""
        # event one
        e1_name = self.event_one_name
        e1_country = self.event_one_country
        e1_city = self.event_one_city
        # this need be parsed to lat, lon, alt
        e1_location = self.event_one_location
        _e1_location = self._parse_location(e1_location)
        # print(f"_e1_location : {_e1_location}")
        # this need be parsed to julian day / year, month, day, hour, minute, second
        e1_datetime = self.event_one_date_time
        _e1_datetime = self._parse_datetime(e1_datetime)
        # print(f"_e1_datetime : {_e1_datetime}")
        # event two
        e2_name = self.event_two_name
        e2_country = self.event_two_country
        e2_city = self.event_two_city
        e2_location = self.event_two_location
        _e2_location = (
            self._parse_location(e2_location) if e2_location else _e1_location
        )
        # print(f"_e2_location : {_e2_location}")
        e2_datetime = self.event_two_date_time
        _e2_datetime = (
            self._parse_datetime(e2_datetime) if e2_datetime else _e1_datetime
        )
        # print(f"_e2_datetime : {_e2_datetime}")

        self.notify_user(
            message="data ready",
            source="swecore",
            level="debug",
        )

        return {
            e1_name: [e1_country, e1_city, _e1_location, _e1_datetime],
            e2_name: [
                e2_country or e1_country,
                e2_city or e1_city,
                _e2_location or _e1_location,
                _e2_datetime or _e1_datetime,
            ],
        }

    def _parse_location(
        self, location_str: str
    ) -> Optional[Dict[str, Union[float, int]]]:
        """parse location string"""
        try:
            # expected format : lat, lon, alt or lat, lon
            parts = location_str.strip().lower().split(" ")
            if len(parts) < 8:
                return None
            # latitide
            lat_deg = float(parts[0])
            lat_min = float(parts[1])
            lat_sec = float(parts[2])
            lat_dir = parts[3]
            # longitude
            lon_deg = float(parts[4])
            lon_min = float(parts[5])
            lon_sec = float(parts[6])
            lon_dir = parts[7]

            alt = 0
            if len(parts) == 9:
                alt = int(parts[8])
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
                "alt": alt,
            }
        except Exception as e:
            self.notify_user(
                message=f"error parsing location '{location_str}'\n\tstr({e})",
                source="swepositions",
                level="error",
            )
            return None

    def _parse_datetime(self, dt_str: str) -> Optional[float]:
        """parse datetime string"""
        try:
            # expected format : YYYY-MM-DD HH:MM:SS
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            # julianday with swisseph
            jd_ut_swe = swe.julday(
                dt.year, dt.month, dt.day, dt.hour + dt.minute / 60 + dt.second / 3600
            )
            # print(f"_parsedatetime : jd_ut_swe : {jd_ut_swe}")
            return jd_ut_swe

        except Exception as e:
            print(f"error parsing datetime : {e}")

            return None

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
