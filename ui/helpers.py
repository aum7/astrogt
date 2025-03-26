# ruff: noqa: E402
import swisseph as swe
import pytz
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
from typing import Optional, Dict, Union
from math import modf


def _create_icon(manager, icons_path, icon_name):
    return Gtk.Image.new_from_file(f"{icons_path}{icon_name}")


def _decimal_to_dms(decimal):
    """convert decimal number to degree-minute-second"""
    min_, deg_ = modf(decimal)
    sec_, _ = modf(min_ * 60)
    deg = int(deg_)
    min = int(min_ * 60)
    sec = int(sec_ * 60)

    return deg, min, sec


def _on_time_now(manager):
    """set time now for selected event location & update entry"""
    manager._notify.debug(
        "collecting application / computer time ...",
        source="_on_time_now",
        route=["terminal", "user"],
        timeout=1,
    )
    # get datetime compoter now
    dt_app = datetime.now()
    # puf! puf! to utc
    dt_utc = dt_app.astimezone(pytz.utc)
    # format & set new value
    dt_utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
    manager._notify.debug(
        f"\ntime now dt_app : {dt_app}"
        f"\n\tformatted : {dt_app.strftime('%Y-%m-%d %H:%M:%S %z (%Z)')}"
        f"\ntime now dt_utc : {dt_utc}"
        f"\n\tformatted : {dt_utc.strftime('%Y-%m-%d %H:%M:%S %z (%Z)')}",
        source="_on_time_now",
        route=["terminal", "user"],
        timeout=1,
    )
    manager._notify.debug(
        "sending dt_utc_str to _parse_datetime",
        source="_on_time_now",
        route=["terminal", "user"],
    )
    manager._notify.debug(
        f"dt_utc_str : {dt_utc_str}",
        source="_on_time_now",
        route=["terminal", "user"],
    )
    _parse_datetime(manager, dt_utc_str, is_utc=True)


def _process_event(manager, event_name: Optional[str]) -> None:
    """get data for event on datetime entry"""
    if event_name is None or event_name == "":
        event_name = manager.selected_event
    if event_name == "event one":
        event_one_data = (
            manager.EVENT_ONE.collect_event_data() if manager.EVENT_ONE else None
        )
        manager.swe_core.process_event_one(event_one_data)
    elif event_name == "event two":
        event_two_data = (
            manager.EVENT_TWO.collect_event_data() if manager.EVENT_TWO else None
        )
        manager.swe_core.process_event_two(event_two_data)


def _event_selection(gesture, n_press, x, y, event_name, manager):
    """handle event selection"""
    # todo merge with event_toggle_selected
    if manager.selected_event != event_name:
        manager.selected_event = event_name
        if manager.selected_event == "event one":
            # todo comment
            print(f"event_selection : {manager.selected_event} selected")
            manager.clp_event_two.remove_title_css_class("label-event-selected")
            manager.clp_event_one.add_title_css_class("label-event-selected")
        if manager.selected_event == "event two":
            # todo comment
            print(f"event_selection : {manager.selected_event} selected")
            manager.clp_event_one.remove_title_css_class("label-event-selected")
            manager.clp_event_two.add_title_css_class("label-event-selected")


def _change_event_time(manager, sec_delta):
    """adjust event time by given seconds"""
    # get active entry : event one or two
    if manager.selected_event == "event one" and manager.EVENT_ONE:
        entry = manager.EVENT_ONE.date_time
        caller = "e1"
    elif manager.selected_event == "event two" and manager.EVENT_TWO:
        entry = manager.EVENT_TWO.date_time
        caller = "e2"
    else:
        entry = None
        caller = None
        manager._notify.debug(
            "no event selected for entry",
            source="_change_event_time",
            route=["terminal", "user"],
        )
    if not entry:
        return
    # get current datetime
    current_text = entry.get_text().strip()
    # if empty, use current utc
    if not current_text:
        manager._notify.warning(
            "datetime None : using utc",
            source="_change_event_time",
            route=["terminal", "user"],
        )
        current_naive = datetime.now().replace(microsecond=0)
    else:
        try:
            # parse datetime as naive
            current_naive = datetime.strptime(current_text, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            manager._notify.error(
                "invalid datetime format, using datetime now utc",
                source="_change_event_time",
                route=["terminal", "user"],
            )
            current_naive = datetime.now().replace(microsecond=0)
    # apply delta to naive datetime
    new_naive = current_naive + timedelta(seconds=int(sec_delta))
    # format & set new value
    new_text = new_naive.strftime("%Y-%m-%d %H:%M:%S")
    entry.set_text(new_text)
    # trigger entry activate signal
    # entry.activate()
    # parse datetime directly
    _parse_datetime(manager, new_text, caller=caller, is_utc=False)


def _change_time_period(
    manager,
    widget: Optional[Gtk.Widget] = None,
    data: Optional[str] = None,
    direction=1,
):
    """helper function to change time period ; direction -1 / 1 for previous / next"""
    # get list of periods
    period_keys = list(manager.CHANGE_TIME_PERIODS.keys())
    period_values = list(manager.CHANGE_TIME_PERIODS.values())
    # get current selected
    current_value = manager.time_periods_list[manager.ddn_time_periods.get_selected()]
    current_key = next(
        (k for k, v in manager.CHANGE_TIME_PERIODS.items() if v == current_value), None
    )
    if current_key:
        current_index = period_keys.index(current_key)
        new_index = (current_index + direction) % len(period_keys)
        new_key = period_keys[new_index]
        new_value = manager.CHANGE_TIME_PERIODS[new_key]
        # set new value
        dropdown_index = period_values.index(new_value)
        manager.ddn_time_periods.set_selected(dropdown_index)
        # notify new value
        # manager._notify.info(
        #     f"selected period : {new_value}", source="time change", timeout=3
        # )
        seconds = new_key.split("_")[-1]
        manager.CHANGE_TIME_SELECTED = seconds


def _parse_location(
    manager, location_str: str
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
        manager._notify.error(
            message=f"error parsing location '{location_str}'\n\t{e}",
            source="_parselocation",
            route=["terminal", "user"],
        )
        return None


def _parse_datetime(
    manager,
    dt_str: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    caller: Optional[str] = None,
    is_utc: bool = False,
) -> Optional[float]:
    """parse datetime string & return julian day utc"""
    if not dt_str:
        manager._notify.error(
            "datetime string is None : exiting ...",
            source="_parsedatetime",
            route=["terminal", "user"],
        )
        return None
    # we have string
    manager._notify.debug(
        f"received dt_str : {dt_str}",
        source="_parsedatetime",
        route=["terminal", "user"],
    )
    # dt_str_tz = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S %z (%Z)")
    # dt_str_no_tz = dt_str_tz.strftime("%Y-%m-%d %H:%M:%S")
    # manager._notify.debug(
    #     f"\n\ndt_str_tz : {dt_str_tz}\ndt_str_no_tz : {dt_str_no_tz}",
    #     source="_parsedatetime",
    #     route=["terminal", "user"],
    # )
    # utc_dt = None
    try:
        # expected format without timezone : YYYY-MM-DD HH:MM:SS
        dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        manager._notify.debug(
            f"dt_naive : {dt_naive.strftime('%Y-%m-%d %H:%M:%S')}",
            source="_parsedatetime",
            route=["terminal", "user"],
        )
        dt_utc = None
        # utc_dt = None
        if is_utc:
            # computer time in  utc, can be anywhere on planet earth
            # we have datetime utc > calculate julianday
            dt_utc = pytz.utc.localize(dt_naive)
            # utc_dt = pytz.utc.localize(dt_naive)
            # dt_utc = dt_naive.replace(tzinfo=pytz.utc)
            manager._notify.debug(
                # f"using received utc_dt (localized) : {utc_dt.strftime('%Y-%m-%d %H:%M:%S)')}",
                f"using received dt_utc (localized) : {dt_utc.strftime('%Y-%m-%d %H:%M:%S')}",
                source="_parsedatetime",
                route=["terminal", "user"],
            )
        # else we need convert event location to utc
        else:
            # check lat & lon
            if (lat is None or lon is None) and caller:
                if caller == "e1":
                    location = _parse_location(manager, manager.event_one_location)
                elif caller == "e2":
                    location = _parse_location(manager, manager.event_two_location)
                else:
                    location = None
                if location:
                    lat = location["lat"]
                    lon = location["lon"]
            # convert to timezone-aware datetime
            if lat is not None and lon is not None:
                # find timezone of location
                tzf = TimezoneFinder()
                timezone_str = tzf.timezone_at(lat=lat, lng=lon)
                manager._notify.debug(
                    f"timezone_str : {timezone_str}",
                    source="_parsedatetime",
                    route=["terminal", "user"],
                )
                if timezone_str:
                    timezone = pytz.timezone(timezone_str)  # ok
                    manager._notify.debug(
                        f"timezone : {timezone}",
                        source="_parsedatetime",
                        route=["terminal", "user"],
                    )
                    # convert to timezone-aware datetime : format differs from ours
                    # dt_event = utc_dt.astimezone(timezone)
                    dt_event = timezone.localize(dt_naive)
                    dt_event_str = dt_event.strftime("%Y-%m-%d %H:%M:%S %z (%Z)")
                    manager._notify.debug(
                        f"dt_event_str (localized naive) :\t{dt_event_str}",
                        source="_parsedatetime",
                        route=["terminal", "user"],
                    )
                    # to utc
                    # HERE
                    dt_utc = dt_event.astimezone(timezone)
                    # dt_utc = dt_event.astimezone(pytz.utc)
                    dt_utc_event_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S %z (%Z)")
                    # print(f"dt_utc_str : {dt_utc_str}")
                    manager._notify.debug(
                        f"\ndt_utc for event (astimezone) :\t{dt_utc_event_str}"
                        f"\n\t\tdt_utc_event_str :\t{dt_utc_event_str}",
                        source="_parsedatetime",
                        route=["terminal", "user"],
                    )
                else:
                    # timezone not found : fallback - should be logged
                    manager._notify.warning(
                        "timezone not found, using utc",
                        source="_parsedatetime",
                        route=["terminal", "user"],
                    )
                    dt_utc = dt_naive.replace(tzinfo=pytz.utc)
            else:
                # no coordinates provided : fallback - should be logged
                manager._notify.warning(
                    "coordinates missing, using utc",
                    source="_parsedatetime",
                    route=["terminal", "user"],
                )
                # conver original string
                # dt_str_utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S %z (%Z)")
                dt_utc = dt_naive.replace(tzinfo=pytz.utc)

        # update entry text if needed
        # __set_entry_text(manager, dt_utc, caller)

        # julianday with swisseph
        jd_ut = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600,
        )
        manager._notify.debug(
            f"jd_ut calculated : {jd_ut}",
            source="_parsedatetime",
            route=["terminal", "user"],
        )
        return jd_ut

    except Exception as e:
        manager._notify.error(
            f"error parsing datetime\n\t{e}",
            source="_parsedatetime",
        )
        # print(f"error parsing datetime\n\t{e}")
        return None


def __set_entry_text(manager, dt_utc, caller):
    if (
        caller == "e1"
        and hasattr(manager, "EVENT_ONE")
        and manager.EVENT_ONE
        and hasattr(manager.EVENT_ONE, "date_time")
    ):
        manager.EVENT_ONE.date_time.set_text(dt_utc.strftime("%Y-%m-%d %H:%M:%S"))
    elif (
        caller == "e2"
        and hasattr(manager, "EVENT_TWO")
        and manager.EVENT_TWO
        and hasattr(manager.EVENT_TWO, "date_time")
    ):
        manager.EVENT_TWO.date_time.set_text(dt_utc.strftime("%Y-%m-%d %H:%M:%S"))
