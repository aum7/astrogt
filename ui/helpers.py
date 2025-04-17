# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional
from math import modf


def _buttons_from_dict(
    manager,
    buttons_dict=None,
    icons_path: Optional[str] = None,
    icon_size: Optional[int] = None,
    pop_context: bool = False,
    pos: Optional[str] = None,
):
    """create buttons from dictionary with icon and tooltip"""
    icons_folder = "ui/imgs/icons/hicolor/scalable/"
    icons_path_cpl = icons_folder + icons_path if icons_path else icons_folder
    buttons = []

    for button_name, tooltip in (buttons_dict or manager.TOOLS_BUTTONS).items():
        button = Gtk.Button()
        button.add_css_class("button-pane")
        button.set_tooltip_text(tooltip)
        icon = Gtk.Image.new_from_file(f"{icons_path_cpl}{button_name}.svg")
        if icon_size:
            icon.set_pixel_size(icon_size)
        else:
            icon.set_icon_size(Gtk.IconSize.NORMAL)
        button.set_child(icon)

        callback_name = f"obc_{button_name}"
        if hasattr(manager, callback_name):
            if pop_context and pos is not None:
                button.connect(
                    "clicked",
                    lambda btn,
                    name=button_name,
                    pos=pos: manager.handle_context_action(btn, name, pos),
                )
            else:
                button.connect("clicked", getattr(manager, callback_name), button_name)
        else:
            button.connect("clicked", manager.obc_default, button_name)

        buttons.append(button)
    return buttons


def _event_selection(manager, gesture, n_press, x, y, event_name):
    """handle event selection"""
    if manager._app.selected_event != event_name:
        manager._app.selected_event = event_name
        if manager._app.selected_event == "event one":
            manager.clp_event_two.remove_title_css_class("label-event-selected")
            manager.clp_event_one.add_title_css_class("label-event-selected")
        if manager._app.selected_event == "event two":
            manager.clp_event_one.remove_title_css_class("label-event-selected")
            manager.clp_event_two.add_title_css_class("label-event-selected")
        manager._notify.debug(f"{manager._app.selected_event} selected")


def _decimal_to_dms(decimal):
    """convert decimal number to degree-minute-second"""
    min_, deg_ = modf(decimal)
    sec_, _ = modf(min_ * 60)
    deg = int(deg_)
    min = int(min_ * 60)
    sec = int(sec_ * 60)

    return deg, min, sec


# def _on_time_now(manager):
#     """get time now (utc) for computer / app location"""
#     if manager._app.selected_event == "event one" and manager._app.EVENT_ONE:
#         entry = manager._app.EVENT_ONE.date_time
#         manager._app.EVENT_ONE.is_hotkey_now = True
#         manager._app.EVENT_ONE.on_datetime_change(entry)
#     elif manager._app.selected_event == "event two" and manager._app.EVENT_TWO:
#         entry = manager._app.EVENT_TWO.date_time
#         manager._app.EVENT_TWO.is_hotkey_now = True
#         manager._app.EVENT_TWO.on_datetime_change(entry)
