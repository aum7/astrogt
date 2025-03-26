# ruff: noqa: E402
import pytz
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from math import modf
from datetime import datetime, timezone, timedelta
from typing import Optional


def _create_icon(manager, icons_path, icon_name):
    # icons_path = icons_path
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
    print(f"ontimenow : {manager.selected_event}")
    if manager.selected_event == "event one" and manager.EVENT_ONE:
        current_utc = datetime.now(pytz.utc)
        formatted_utc = current_utc.strftime("%Y-%m-%d %H:%M:%S")
        manager.EVENT_ONE.date_time.set_text(formatted_utc)
        manager.EVENT_ONE.on_date_time_change(manager.EVENT_ONE.date_time)
    elif manager.selected_event == "event two" and manager.EVENT_TWO:
        current_utc = datetime.now(pytz.utc)
        formatted_utc = current_utc.strftime("%Y-%m-%d %H:%M:%S")
        manager.EVENT_TWO.date_time.set_text(formatted_utc)
        manager.EVENT_TWO.on_date_time_change(manager.EVENT_TWO.date_time)


def _process_event(manager, event_name: Optional[str]) -> None:
    """get data for event on datetime entry"""
    print("_process_event_data called")
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
    elif manager.selected_event == "event two" and manager.EVENT_TWO:
        entry = manager.EVENT_TWO.date_time
    else:
        entry = None
        manager._notify.debug(
            "adjusteventtime : no event selected for entry",
            source="sidepane",
            route=["terminal"],
        )
    if not entry:
        return
    # get current datetime
    current_text = entry.get_text().strip()
    # if empty, use current utc
    if not current_text:
        manager._notify.warning(
            "dadjusteventtime : datetime None : using utc",
            source="sidepane [adjust_event_time]",
        )
        current_utc = datetime.now(timezone.utc)
    else:
        try:
            # parse datetime
            current_utc = datetime.strptime(current_text, "%Y-%m-%d %H:%M:%S")
            # assume utc todo
            current_utc = current_utc.replace(tzinfo=timezone.utc)
        except ValueError:
            manager._notify.error(
                "adjusteventtime : invalid datetime format, using datetime.now utc",
                source="sidepane",
            )
            current_utc = datetime.now(timezone.utc)
    # apply delta
    current_utc = current_utc + timedelta(seconds=int(sec_delta))
    # format & set new value
    new_text = current_utc.strftime("%Y-%m-%d %H:%M:%S")
    entry.set_text(new_text)
    # trigger entry activate signal
    entry.activate()


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
