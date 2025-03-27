# ruff: noqa: E402
import swisseph as swe
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
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
    # def _change_event_time(manager, sec_delta, direction=1):
    """adjust event time by given seconds"""
    # get selected entry : event one or two
    if manager.selected_event == "event one" and manager.EVENT_ONE:
        entry = manager.EVENT_ONE.date_time
        caller = "e1"
    elif manager.selected_event == "event two" and manager.EVENT_TWO:
        entry = manager.EVENT_TWO.date_time
        caller = "e2"
    # get current datetime
    current_text = entry.get_text().strip()
    # if empty, use current utc
    if not current_text:
        manager._notify.warning(
            "datetime none : using computer time now",
            source="_change_event_time",
            route=["terminal"],
        )
        # datetime now with rounded seconds
        current_naive = datetime.now().replace(microsecond=0)
    else:
        try:
            # parse current text as naive datetime
            current_naive = datetime.strptime(current_text, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            manager._notify.error(
                "invalid datetime format, using computer time now",
                source="_change_event_time",
                route=["terminal"],
            )
            # datetime now with rounded seconds
            current_naive = datetime.now().replace(microsecond=0)
    # year & month : changing by seconds does not account leap years
    # todo fwd works ok, bwd changes day of month : bug in datetime ?
    # if int(sec_delta) == 315360000:  # 10 years
    #     if direction == 1:
    #         new_naive = current_naive.replace(year=current_naive.year + 10)
    #     else:
    #         new_naive = current_naive.replace(year=current_naive.year - 10)
    # if int(sec_delta) == 31536000:  # year
    #     if direction == 1:
    #         new_naive = current_naive.replace(year=current_naive.year + 1)
    #     else:
    #         new_naive = current_naive.replace(year=current_naive.year - 1)
    # else:
    # apply delta to naive datetime
    new_naive = current_naive + timedelta(seconds=int(sec_delta))
    # set new value formatted
    new_text = new_naive.strftime("%Y-%m-%d %H:%M:%S")
    entry.set_text(new_text)
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


def _on_time_now(manager):
    """get time now (utc) for computer / app location & send it to _parse_datetime"""
    # get computer time in utc
    # dt_utc = datetime.now(timezone.utc)
    # dt_utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
    # manager._notify.debug(
    #     f"---------\nsending dt_utc_str ({dt_utc_str}) to _parse_datetime",
    #     source="_on_time_now",
    #     route=["terminal"],
    #     timeout=1,
    # )
    _parse_datetime(manager, dt_str="", is_utc=True)


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
            route=["terminal"],
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
    if not dt_str and not is_utc:
        manager._notify.error(
            f"datetime string is none ({caller}): exiting ...",
            source="_parsedatetime",
            route=["terminal"],
        )
        return None
    event = manager.selected_event
    _event = None
    timezone_str = None
    if event in ["event one", "event two"]:
        _event = getattr(manager, event.upper().replace(" ", "_"))
        # get latitude & longitude
    if lat is None or lon is None:
        _location = event.location.get_text()
        location = _parse_location(manager, _location) if _location else {}
        if location:
            lat, lon = location["lat"], location["lon"]
        # get timezon info
        if lat is not None and lon is not None:
            tzf = TimezoneFinder()
            timezone_str = tzf.timezone_at(lat=lat, lng=lon)
        if not timezone_str:
            # timezone not found : fallback - should be logged
            manager._notify.error(
                "timezone not found, exiting ...",
                source="_parsedatetime",
                route=["all"],
            )
            return None
    try:
        if is_utc:
            # computer time in utc, can be anywhere on planet earth
            dt_utc = datetime.now(timezone.utc)
            # need update entry text
            if _event:
                _event.date_time.set_text(dt_utc.strftime("%Y-%m-%d %H:%M:%S"))
                manager._notify.debug(
                    f"\n\tsetting {event} text: {dt_utc.strftime('%Y-%m-%d %H:%M:%S')}",
                    source="_parsedatetime",
                    route=["terminal"],
                )
            manager._notify.debug(
                f"\n\tusing dt_utc (now) : {dt_utc.strftime('%Y-%m-%d %H:%M:%S')}",
                source="_parsedatetime",
                route=["terminal"],
            )
        elif dt_str:
            # parse naive datetim
            dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            # manager._notify.debug(
            #     f"---------\n\treceived dt_naive : {dt_naive.strftime('%Y-%m-%d %H:%M:%S')}"
            #     f"\n\tis_utc : {is_utc}",
            #     source="_parsedatetime",
            #     route=["terminal"],
            # )
            # else we need convert event location to utc
            if timezone_str:
                dt_event = dt_naive.astimezone(ZoneInfo(timezone_str))
            manager._notify.debug(
                f"\n\tdt_event (astimezone({timezone_str})) : "
                f"{dt_event.strftime('%Y-%m-%d %H:%M:%S %z (%Z)')}"
                f"\n\toffset : {dt_event.utcoffset()} | "
                f"tz : {dt_event.tzinfo} | dst : {dt_event.dst()}",
                source="_parsedatetime",
                route=["terminal"],
            )
            dt_utc = dt_event.astimezone(timezone.utc)
            manager._notify.debug(
                f"\n\tdt_utc (astimezone) :"
                f"\t{dt_utc.strftime('%Y-%m-%d %H:%M:%S %z (%Z)')}",
                source="_parsedatetime",
                route=["terminal"],
            )
        else:
            # no timezone found : set naive datetime
            # todo no timezone = use event one
            dt_utc = datetime.now(timezone.utc)
            manager._notify.warning(
                "no timezone found (event two ?), using datetime utc",
                source="_parsedatetime",
                route=["terminal"],
            )
        # julianday with swisseph
        jd_ut = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600,
        )
        manager._notify.debug(
            f"\n\tdt_utc ({dt_utc}) : jd_ut calculated : {jd_ut}",
            source="_parsedatetime",
            route=["terminal"],
        )
        return jd_ut

    except Exception as e:
        manager._notify.error(
            f"error parsing datetime\n\t{e}",
            source="_parsedatetime",
            route=["terminal"],
        )
        return None
