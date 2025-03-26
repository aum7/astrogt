# ruff: noqa: E402
import os
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject  # type: ignore
from user.settings.settings import SWE_FLAG  # ,OBJECTS
from ui.helpers import _parse_location, _parse_datetime


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

    def process_event_one(self, event=None):
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

    def process_event_two(self, event=None):
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
        e1_location = _parse_location(self, self.event_one_location)
        e1_lat = None
        e1_lon = None
        e1_alt = None
        if e1_location:
            e1_lat = e1_location["lat"]
            e1_lon = e1_location["lon"]
            e1_alt = e1_location["alt"]
        # this need be parsed to julian day
        e1_datetime = _parse_datetime(
            self, self.event_one_date_time, e1_lat, e1_lon, caller="e1"
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
        e2_location = _parse_location(self, self.event_two_location)
        e2_lat = None
        e2_lon = None
        e2_alt = None
        if e2_location:
            e2_lat = e2_location["lat"]
            e2_lon = e2_location["lon"]
            e2_alt = e2_location["alt"]
        # this need be parsed to julian day
        e2_datetime = _parse_datetime(
            self, self.event_two_date_time, e2_lat, e2_lon, caller="e2"
        )
        e2_data = [e2_name, e2_country, e2_city, e2_lat, e2_lon, e2_alt, e2_datetime]
        # store data as attribute
        self.swe_e2_data = e2_data
        # self._notify.debug("event 2 data ready -------", source="swecore")
        return e2_data

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
