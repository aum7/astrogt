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
        button.add_css_class("button-change-time")
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
    if manager.app.selected_event != event_name:
        manager.app.selected_event = event_name
        if manager.app.selected_event == "e1":
            clp = manager.clp_event_one
            other_clp = manager.clp_event_two
        if manager.app.selected_event == "e2":
            clp = manager.clp_event_two
            other_clp = manager.clp_event_one
        other_clp.remove_title_css_class("label-event-selected")
        clp.add_title_css_class("label-event-selected")
        manager.notify.debug(
            f"{manager.app.selected_event} selected",
            source="helpers",
            route=["terminal"],
        )


def _decimal_to_dms(decimal):
    """convert decimal number to degree-minute-second"""
    min_, deg_ = modf(decimal)
    sec_, _ = modf(min_ * 60)
    deg = int(deg_)
    min = int(min_ * 60)
    sec = int(sec_ * 60)

    return deg, min, sec


def _decimal_to_hms(decimal):
    """convert decimal hour to hour"""
    H = int(decimal)
    M = int((decimal - H) * 60)
    S = int((decimal - H - M / 60) * 3600)
    return H, M, S


def _decimal_to_ra(decimal):
    # convert circle degrees into right ascension h-m-s
    hour = decimal / 15.0
    H = int(hour)
    minute = (hour - H) * 60
    M = int(minute)
    S = int(round((minute - M) * 60))
    return H, M, S
