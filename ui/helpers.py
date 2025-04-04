# ruff: noqa: E402
import re
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from math import modf
from sweph.swetime import swetime_to_jd


def _create_icon(manager, icons_path, icon_name):
    return Gtk.Image.new_from_file(f"{icons_path}{icon_name}")


def _event_selection(manager, gesture, n_press, x, y, event_name):
    """handle event selection"""
    # todo merge with event_toggle_selected
    if manager._app.selected_event != event_name:
        manager._app.selected_event = event_name
        if manager._app.selected_event == "event one":
            manager.clp_event_two.remove_title_css_class("label-event-selected")
            manager.clp_event_one.add_title_css_class("label-event-selected")
        if manager._app.selected_event == "event two":
            manager.clp_event_one.remove_title_css_class("label-event-selected")
            manager.clp_event_two.add_title_css_class("label-event-selected")
        manager._notify.debug(
            f"\thotkey | button : {manager._app.selected_event} selected"
        )


def _decimal_to_dms(decimal):
    """convert decimal number to degree-minute-second"""
    min_, deg_ = modf(decimal)
    sec_, _ = modf(min_ * 60)
    deg = int(deg_)
    min = int(min_ * 60)
    sec = int(sec_ * 60)

    return deg, min, sec


def _on_time_now(manager):
    """get time now (utc) for computer / app location"""
    if manager._app.selected_event == "event one" and manager._app.EVENT_ONE:
        entry = manager._app.EVENT_ONE.date_time
        manager._app.EVENT_ONE.is_hotkey_now = True
        manager._app.EVENT_ONE.on_datetime_change(entry)
    elif manager._app.selected_event == "event two" and manager._app.EVENT_TWO:
        entry = manager._app.EVENT_TWO.date_time
        manager._app.EVENT_TWO.is_hotkey_now = True
        manager._app.EVENT_TWO.on_datetime_change(entry)


def _validate_datetime(manager, date_time):
    # check characters todo also add local time
    valid_chars = set("0123456789 -:jg")
    invalid_chars = set(date_time) - valid_chars
    msg_negative_year = ""
    try:
        if invalid_chars:
            raise ValueError(f"characters {sorted(invalid_chars)} not allowed")
        is_year_negative = date_time.lstrip().startswith("-")
        parts = [p for p in re.split(r"[- :]+", date_time) if p]
        # todo allow for date only
        if len(parts) < 5 or len(parts) > 6:
            raise ValueError(
                "wrong data count : 6 or 5 (if no seconds) time units expected"
                "\n\tie 1999 11 12 13 14 : set time to 12 00 or 00 00 if unknown"
            )
        y_, m_, d_, h_, mi_, s_ = map(int, parts)
        # year, month, day, hour, minute, second = map(int, parts)
        if is_year_negative:
            # year = -abs(year)
            msg_negative_year = f"found negative year : {y_}\n"
        else:
            msg_negative_year = ""
        # swiseph year range
        if not -13200 <= y_ <= 17191:
            raise ValueError(f"year {y_} out of sweph range (-13200 - 17191)")
        # except ValueError as e:
        #     raise ValueError(e)
        if len(parts) == 5:
            # add seconds
            parts.append("00")
        # check if swetime is valid
        calendar = b"g"
        is_valid, jd, swe_corr = swetime_to_jd(
            y_, m_, d_, hour=h_, min=mi_, sec=s_, calendar=calendar
        )
        if not is_valid:
            raise ValueError(
                "_validatedatetime : swetimetojd is not valid\n"
                f"using swe_corr anyway : {swe_corr}"
            )
        corr_y, corr_m, corr_d, corr_h_ = swe_corr
        print(
            f"_validatedatetime : swetimetojd is valid\ncorrected values : {corr_y} | {corr_m} | {corr_d} | {corr_h_}"
        )
        corr_h = int(corr_h_)
        corr_min = int((corr_h_ - corr_h) * 60)
        corr_sec = int(round((((corr_h_ - corr_h) * 60) - corr_min) * 60))
        manager._notify.debug(
            f"\n\tdate-time as corrected : {corr_y}-{corr_m}-{corr_d}"
            f"{corr_h}:{corr_min}:{corr_sec}",
            source="helpers",
            route=["terminal", "user"],
        )
    except ValueError as e:
        manager._notify.warning(
            f"{date_time}\n\terror\n\t{e}\n\t{msg_negative_year}",
            source="helpers",
            route=["terminal", "user"],
        )
        return False
    return jd, corr_y, corr_m, corr_d, corr_h, corr_min, corr_sec
