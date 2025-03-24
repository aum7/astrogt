# ruff: noqa: E402
import os
import swisseph as swe
import gi
import pytz

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject  # type: ignore
from typing import Optional, Union, Dict
from user.settings.settings import SWE_FLAG  # ,OBJECTS
from datetime import datetime
from timezonefinder import TimezoneFinder


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

    def __init__(self, app=None):
        super().__init__()
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        self._signal = self._app.signal_manager
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

    def get_event_one_data(self, event=None):
        if event:
            print("processing event one")
            if (
                not event["name"]
                or not event["country"]
                or not event["city"]
                or not event["location"]
                or not event["date_time"]
            ):
                self._notify.warning(
                    message="event one : data missing",
                    source="swecore",
                )
                return {}
            # check if data has changed
            if (
                event["name"] != self.event_one_name
                or event["country"] != self.event_one_country
                or event["city"] != self.event_one_city
                or event["location"] != self.event_one_location
                or event["date_time"] != self.event_one_date_time
            ):
                # event one data has changed
                # self._notify.info(
                #     message="event one : data changed ...",
                #     source="swecore",
                # )
                # data received
                self.event_one_name = event["name"]
                self.event_one_country = event["country"]
                self.event_one_city = event["city"]
                self.event_one_location = event["location"]
                self.event_one_date_time = event["date_time"]
                # process data
                data = self.event_one_swe_ready()
                # emit signal for positions, houses, aspects etc
                self._signal._emit("event-one-changed", data)
            else:
                self._notify.info(
                    message="event one : data NOT changed",
                    source="swecore",
                )

    def get_event_two_data(self, event=None):
        if event:
            print("processing event two")
            # if data nor provided, use event one data
            if not event["name"]:
                event["name"] = self.event_one_name
            if not event["country"]:
                event["country"] = self.event_one_country
            if not event["city"]:
                event["city"] = self.event_one_city
            if not event["location"]:
                event["location"] = self.event_one_location
            # for event two only datetime is mandatory
            if not event["date_time"]:
                self._notify.info(
                    message="event two : datetime missing : setting to event one",
                    source="swecore",
                    timeout=1,
                )
                event["date_time"] = self.event_one_date_time
            # check if data has changed
            if (
                event["name"] != self.event_two_name
                or event["country"] != self.event_two_country
                or event["city"] != self.event_two_city
                or event["location"] != self.event_two_location
                or event["date_time"] != self.event_two_date_time
            ):
                # self._notify.info(
                #     message="event two : data changed ...",
                #     source="swecore",
                # )
                # data received
                self.event_two_name = event["name"]
                self.event_two_country = event["country"]
                self.event_two_city = event["city"]
                self.event_two_location = event["location"]
                self.event_two_date_time = event["date_time"]
                # process data
                data = self.event_two_swe_ready()
                # emit signal for positions, houses, aspects etc
                self._signal._emit("event-two-changed", data)
            else:
                self._notify.info(
                    message="event two : data NOT changed",
                    source="swecore",
                )

    def event_one_swe_ready(self):
        """prepare event one data for swe calculations"""
        e1_name = self.event_one_name
        e1_country = self.event_one_country
        e1_city = self.event_one_city
        # this need be parsed to lat, lon, alt
        e1_location = self._parse_location(self.event_one_location)
        e1_lat = None
        e1_lon = None
        e1_alt = None
        if e1_location:
            e1_lat = e1_location["lat"]
            e1_lon = e1_location["lon"]
            e1_alt = e1_location["alt"]
        # this need be parsed to julian day
        e1_datetime = self._parse_datetime(
            self.event_one_date_time, e1_lat, e1_lon, caller="e1"
        )
        e1_data = [e1_name, e1_country, e1_city, e1_lat, e1_lon, e1_alt, e1_datetime]
        # store data as attribute
        self.swe_e1_data = e1_data
        # self._notify.debug("event 1 data ready -------", source="swecore")
        return e1_data

    def event_two_swe_ready(self):
        """prepare event two data for swe calculations"""
        e2_name = self.event_two_name
        e2_country = self.event_two_country
        e2_city = self.event_two_city
        # this need be parsed to lat, lon, alt
        e2_location = self._parse_location(self.event_two_location)
        e2_lat = None
        e2_lon = None
        e2_alt = None
        if e2_location:
            e2_lat = e2_location["lat"]
            e2_lon = e2_location["lon"]
            e2_alt = e2_location["alt"]
        # this need be parsed to julian day
        e2_datetime = self._parse_datetime(
            self.event_two_date_time, e2_lat, e2_lon, caller="e2"
        )
        e2_data = [e2_name, e2_country, e2_city, e2_lat, e2_lon, e2_alt, e2_datetime]
        # store data as attribute
        self.swe_e2_data = e2_data
        # self._notify.debug("event 2 data ready -------", source="swecore")
        return e2_data

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

    def _parse_datetime(
        self,
        dt_str: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        caller: Optional[str] = None,
    ) -> Optional[float]:
        """parse datetime string"""
        # print(f"_parsedatetime : dt_str : {dt_str}")
        lat = lat
        lon = lon
        if not dt_str:
            return None
        try:
            # expected format : YYYY-MM-DD HH:MM:SS
            dt_local = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            # check lat & lon
            if (lat is None or lon is None) and caller:
                if caller == "e1":
                    location = self._parse_location(self.event_one_location)
                elif caller == "e2":
                    location = self._parse_location(self.event_two_location)
                else:
                    location = None
                if location:
                    lat = location["lat"]
                    lon = location["lon"]
            # convert to timezone aware datetime
            if lat is not None and lon is not None:
                # find timezone of location
                tf = TimezoneFinder()
                timezone_str = tf.timezone_at(lat=lat, lng=lon)
                if timezone_str:
                    timezone = pytz.timezone(timezone_str)
                    # convert to timezone aware datetime
                    dt_local = timezone.localize(dt_local)
                    # to utc
                    dt_utc = dt_local.astimezone(pytz.utc)
                    dt_utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S %z (%Z)")
                    print(f"dt_utc_str : {dt_utc_str}")
                else:
                    # timezone not found : fallback - should be logged
                    self._notify.warning(
                        "timezone not found, using utc", source="swecore"
                    )
                    dt_utc = dt_local.replace(tzinfo=pytz.utc)
            else:
                # no coordinates provided : fallback - should be logged
                self._notify.warning(
                    "coordinates missing, using utc",
                    source="swecore",
                )
                dt_utc = dt_local.replace(tzinfo=pytz.utc)
            # julianday with swisseph
            jd_ut = swe.julday(
                dt_utc.year,
                dt_utc.month,
                dt_utc.day,
                dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600,
            )
            # print(f"_parsedatetime : jd_ut_swe : {jd_ut_swe}")
            return jd_ut

        except Exception as e:
            self._notify.error(
                f"error parsing datetime\n\t{e}",
                source="swecore",
            )
            # print(f"error parsing datetime\n\t{e}")
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
