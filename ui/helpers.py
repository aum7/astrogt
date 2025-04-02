# ruff: noqa: E402
import re
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from math import modf


def _create_icon(manager, icons_path, icon_name):
    return Gtk.Image.new_from_file(f"{icons_path}{icon_name}")


def _event_selection(manager, gesture, n_press, x, y, event_name):
    """handle event selection"""
    # todo merge with event_toggle_selected
    if manager._app.selected_event != event_name:
        manager._app.selected_event = event_name
        if manager._app.selected_event == "event one":
            # todo comment
            print(f"\tevent_selection : {manager._app.selected_event} selected")
            manager.clp_event_two.remove_title_css_class("label-event-selected")
            manager.clp_event_one.add_title_css_class("label-event-selected")
        if manager._app.selected_event == "event two":
            # todo comment
            print(f"\tevent_selection : {manager._app.selected_event} selected")
            manager.clp_event_one.remove_title_css_class("label-event-selected")
            manager.clp_event_two.add_title_css_class("label-event-selected")


def _on_time_now(manager):
    """get time now (utc) for computer / app location & send it to on_datetime_change"""
    if manager._app.selected_event == "event one" and manager._app.EVENT_ONE:
        entry = manager._app.EVENT_ONE.date_time
        manager._app.EVENT_ONE.is_utc_now = True
        manager._app.EVENT_ONE.on_datetime_change(entry)
    elif manager._app.selected_event == "event two" and manager._app.EVENT_TWO:
        entry = manager._app.EVENT_TWO.date_time
        manager._app.EVENT_TWO.is_utc_now = True
        manager._app.EVENT_TWO.on_datetime_change(entry)


def _decimal_to_dms(decimal):
    """convert decimal number to degree-minute-second"""
    min_, deg_ = modf(decimal)
    sec_, _ = modf(min_ * 60)
    deg = int(deg_)
    min = int(min_ * 60)
    sec = int(sec_ * 60)

    return deg, min, sec


def _validate_datetime(manager, date_time):
    # check characters
    valid_chars = set("0123456789 -:")
    invalid_chars = set(date_time) - valid_chars
    if invalid_chars:
        manager._notify.warning(
            f"date-time : characters {sorted(invalid_chars)} not allowed",
            source="helpers",
            route=["terminal", "user"],
        )
        return False
    is_year_negative = date_time.lstrip().startswith("-")
    # print(f"helpers : year negative : {is_year_negative}")
    parts = [p for p in re.split(r"[- :]+", date_time) if p]
    if len(parts) < 5 or len(parts) > 6:
        manager._notify.warning(
            "wrong data count : 6 or 5 (if no seconds) time units expected"
            "\n\tie 1999 11 12 13 14",
            source="helpers",
            route=["terminal", "user"],
        )
        return False
        # handle year
    try:
        year = int(parts[0])
        if is_year_negative:
            year = -abs(year)
        # print(f"year : {year}")
        # swiseph year range
        if not -13200 <= year <= 17191:
            manager._notify.warning(
                f"year ({year}) out of sweph range (-13.200 - 17.191)",
                source="helpers",
                route=["terminal", "user"],
            )
            return False

    except ValueError:
        manager._notify.error(
            "invalid year format",
            source="helpers",
            route=["terminal", "user"],
        )
        return False

    if len(parts) == 5:
        # add seconds
        parts.append("00")

    _, month, day, hour, minute, second = map(int, parts)

    # check if date_time is valid day
    def is_valid_date(year, month, day):
        day_count_for_month = [
            # 0 added to match number with month
            0,
            31,
            28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ]
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            day_count_for_month[2] = 29

        return 1 <= month <= 12 and 1 <= day <= day_count_for_month[month]

    if not is_valid_date(year, month, day):
        manager._notify.warning(
            f"{year}-{month}-{day} : date not valid"
            "\n\tcheck month & day : ie february has 28 or 29 days",
            source="helpers",
            route=["terminal", "user"],
        )
        return False

    def is_valid_time(hour, minute, second):
        return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59

    if not is_valid_time(hour, minute, second):
        manager._notify.warning(
            f"{hour}:{minute}:{second} : time not valid",
            source="helpers",
            route=["user"],
        )
        return False
    return year, month, day, hour, minute, second
