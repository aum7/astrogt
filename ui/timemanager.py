# ruff: noqa: E402
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder


class TimeManager:
    def __init__(self, app):
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager

    def get_selected(self):
        """get selected event & return entry widget, datetime & location string"""
        selected_ = self._app.selected_event
        event = self._app.EVENT_ONE if selected_ == "event one" else self._app.EVENT_TWO
        if event is None:
            self._notify.error(
                "no event selected, exiting ...",
                source="timemanager",
                route=["terminal"],
            )
            return None
        entry = event.date_time
        name = event.name.get_text().strip()
        dt = event.date_time.get_text().strip()
        location = event.location.get_text().strip()
        self._notify.debug(
            f"\n\tselected event : {name}\n\tdt : {dt}\n\tlocation : {location}",
            source="timemanager",
            route=["terminal"],
        )
        # create object with dt & location attributes
        from collections import namedtuple

        selected = namedtuple("selected", ["event", "entry", "dt", "location"])
        return selected(event, entry, dt, location)

    def parse_location(self):
        """parse location string to lat/lon/alt/timezone dict"""
        try:
            selected = self.get_selected()
            if selected is None:
                return None
            parts = selected.location.lower().split(" ")
            if len(parts) < 8:
                return None
            # latitude
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

            tzf = TimezoneFinder()
            timezone = tzf.timezone_at(lat=lat, lng=lon)

            return {
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "timezone": timezone,
            }
        except Exception as e:
            self._notify.error(
                message=f"error parsing location\n\t{e}",
                source="timemanager",
                route=["terminal"],
            )
            return None

    def parse_datetime(self, is_utc=False):
        """parse datetime string to datetime & return julian day utc"""
        # get location data
        dt_utc = None
        selected = self.get_selected()
        if selected is None:
            return None
        entry = selected.entry
        # entry = self.get_selected.entry
        event_location = self.parse_location()
        try:
            if event_location:
                timezone_ = event_location["timezone"]
            if is_utc:
                # get computer time
                dt_utc_now = datetime.now(timezone.utc).replace(microsecond=0)
                dt_utc = dt_utc_now
                dt_event = dt_utc_now.astimezone(ZoneInfo(timezone_))
                # update datetime entry
                if entry:
                    entry.set_text(dt_event.strftime("%Y-%m-%d %H:%M:%S"))
                self._notify.debug(
                    f"\nparsed application time now utc : {dt_utc_now}"
                    f"\nset event location time now : {dt_event}",
                    source="timemanager",
                    route=["terminal"],
                )
            else:
                # get datetime string
                dt_str = self.get_selected.dt
                # parse to datetime
                dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                # convert to event location timezone
                dt_event = dt_naive.astimezone(timezone_)
                dt_utc = dt_event.astimezone(timezone.utc)
                # update datetime entry
                if entry:
                    entry.set_text(dt_event.strftime("%Y-%m-%d %H:%M:%S"))
                self._notify.debug(
                    f"\nparsed & set event datetime : {dt_event}\ndt_utc : {dt_utc}",
                    source="timemanager",
                    route=["terminal"],
                )
            # calculate julian day utc for swe calculations
            jd_ut = swe.julday(
                dt_utc.year,
                dt_utc.month,
                dt_utc.day,
                dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600,
            )
            return jd_ut

        except Exception as e:
            self._notify.error(
                message=f"error parsing datetime\n\t{e}",
                source="timemanager",
                route=["terminal"],
            )

    def change_time_period(self, direction=1):
        """change time period ; direction -1 / 1 for previous / next"""
        # get list of periods
        period_keys = list(self._app.CHANGE_TIME_PERIODS.keys())
        period_values = list(self._app.CHANGE_TIME_PERIODS.values())
        # get current selected
        # current_value = period_values[
        #     self._app.get_active_window().ddn_time_periods.get_selected()
        # ]
        current_value = self._app.CHANGE_TIME_SELECTED
        # current_key = next(
        #     (k for k, v in self._app.CHANGE_TIME_PERIODS.items() if v == current_value),
        #     None,
        # )
        current_key = next(
            (
                k
                for k in period_keys
                if k.split("__")[-1] == str(self._app.CHANGE_TIME_SELECTED)
            )
        )
        if current_key:
            current_index = period_keys.index(current_key)
            new_index = (current_index + direction) % len(period_keys)
            new_key = period_keys[new_index]
            new_value = self._app.CHANGE_TIME_PERIODS[new_key]
            # set new value
            dropdown_index = period_values.index(new_value)
            self._app.get_active_window().ddn_time_periods.set_selected(dropdown_index)
            # notify new value
            # manager._notify.info(
            #     f"selected period : {new_value}", source="time change", timeout=3
            # )
            seconds = new_key.split("_")[-1]
            self._app.CHANGE_TIME_SELECTED = seconds

    def change_event_time(self, sec_delta):
        """adjust event time by given seconds"""
        # get active entry based on selected event
        selected = self.get_selected()
        if selected is None:
            return None
        if selected.dt == "":
            dt_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            selected.entry.set_text(dt_now)
            self._notify.debug(
                "set datetime to now",
                source="timemanager",
                route=["terminal"],
            )
        entry = selected.entry
        # get current datetime
        current_text = selected.dt
        if not current_text:
            self._notify.error(
                "cannot change time : no datetime : exiting ...",
                source="timemanager",
                route=["terminal"],
            )
            return
        try:
            # increment the naive datetime and let parse_datetime handle rest
            dt_naive = datetime.strptime(current_text, "%Y-%m-%d %H:%M:%S")
            new_naive = dt_naive + timedelta(seconds=int(sec_delta))
            new_text = new_naive.strftime("%Y-%m-%d %H:%M:%S")
            # update entry with new text
            entry.set_text(new_text)
            # process the event with the new time
            # self._app.process_event(self._app.selected_event)
        except ValueError:
            self._notify.error(
                "invalid datetime format, exiting ...",
                source="time_manager",
                route=["terminal"],
            )
            return
