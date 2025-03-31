# ruff: noqa: E402
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
            print(f"event_selection : {manager._app.selected_event} selected")
            manager.clp_event_two.remove_title_css_class("label-event-selected")
            manager.clp_event_one.add_title_css_class("label-event-selected")
        if manager._app.selected_event == "event two":
            # todo comment
            print(f"event_selection : {manager._app.selected_event} selected")
            manager.clp_event_one.remove_title_css_class("label-event-selected")
            manager.clp_event_two.add_title_css_class("label-event-selected")


def _on_time_now(manager):
    """get time now (utc) for computer / app location & send it to parse_datetime"""
    if manager._app.selected_event == "event one" and manager._app.EVENT_ONE:
        entry = manager._app.EVENT_ONE.date_time
        manager._app.EVENT_ONE.is_utc_now = True
        print("ontimenow : got entry for event one : set is_utc true")
        manager._app.EVENT_ONE.on_datetime_change(entry)
    elif manager._app.selected_event == "event two" and manager._app.EVENT_TWO:
        entry = manager._app.EVENT_TWO.date_time
        manager._app.EVENT_TWO.is_utc_now = True
        print("ontimenow : got entry for event two : set is_utc true")
        manager._app.EVENT_TWO.on_datetime_change(entry)


def _decimal_to_dms(decimal):
    """convert decimal number to degree-minute-second"""
    min_, deg_ = modf(decimal)
    sec_, _ = modf(min_ * 60)
    deg = int(deg_)
    min = int(min_ * 60)
    sec = int(sec_ * 60)

    return deg, min, sec
