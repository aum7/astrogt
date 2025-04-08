# ruff: noqa: E402
import re
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Optional
from math import modf
from sweph.swetime import swetime_to_jd


def _buttons_from_dict(
    manager,
    buttons_dict=None,
    icons_path: Optional[str] = None,
    icon_size: Optional[int] = None,
    pop_context: bool = False,
    pos: Optional[str] = None,
):
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


def _validate_datetime(manager, date_time, lon=None):
    """check characters & parse numbers & letters then validate"""
    # mean solar time, aka local mean time (lmt) - modern (utc)
    # true solar time, aka local apparent time (lat) - pre-clock
    # diff = equation of time : historical date lat => to lmt (equation of time)
    valid_chars = set("0123456789 -:ja")
    invalid_chars = set(date_time) - valid_chars
    msg_negative_year = ""
    try:
        if invalid_chars:
            raise ValueError(
                f"characters {sorted(invalid_chars)} not allowed"
                "\n\twe accept : 0123456789 -:ja"
                "\n\tj = julian calendar (gregorian = default)"
                "\n\ta = local apparent time (mean = default)"
            )
        is_year_negative = date_time.lstrip().startswith("-")
        print(f"negative year : {is_year_negative}")
        parts = [p for p in re.split(r"[- :]+", date_time) if p]
        # parts = [p for p in parts if p]
        print(f"parts 2 : {parts}")
        # split into numbers & flags : year-month-day are manadatory
        nums = []
        flags = []
        for p in parts:
            if isinstance(p, str) and p.isdigit():
                nums.append(int(p))
            elif isinstance(p, str) and p.isalpha():
                flags.append(p.lower())
        if len(nums) < 3:
            raise ValueError(
                "wrong data count : year-month-day are mandatory"
                "\n\tie 1999 11 12 or 1999 11 12 13 14 00"
                "\nalso allowed j(ulian) | g(regorian) calendar & local mean | apparent time"
            )
        y_ = -nums[0] if is_year_negative else nums[0]
        m_, d_ = nums[1], nums[2]
        h_ = nums[3] if len(nums) >= 4 else 0
        mi_ = nums[4] if len(nums) >= 5 else 0
        s_ = nums[5] if len(nums) >= 6 else 0
        if is_year_negative:
            msg_negative_year = f"found negative year : {y_}\n"
        else:
            msg_negative_year = ""
        # swiseph year range
        if not -13200 <= y_ <= 17191:
            raise ValueError(f"year {y_} out of sweph range (-13200 - 17191)")
        # check for calendar flag : g(regorian) is default
        calendar = b"g"
        if "j" in flags:
            calendar = b"j"
        # check for time flag : local mean time is default todo
        local_time = "m"  # mean
        if "a" in flags:
            local_time = "a"  # apparent
        # check if swetime is valid
        is_valid, jd, swe_corr = swetime_to_jd(
            manager,
            y_,
            m_,
            d_,
            hour=h_,
            min=mi_,
            sec=s_,
            calendar=calendar,
            local_time=local_time,
            lon=lon,
        )
        if not is_valid:
            raise ValueError(
                "_validatedatetime : swetimetojd is not valid\n"
                f"using swe_corr anyway : {swe_corr}"
            )
        corr_y, corr_m, corr_d, corr_h = swe_corr
        print(
            f"_validatedatetime : swetimetojd is valid\ncorrected values : {corr_y} | {corr_m} | {corr_d} | {corr_h}"
        )
        h_corr = int(corr_h)
        mi_corr = int((corr_h - h_corr) * 60)
        s_corr = int(round((((corr_h - h_corr) * 60) - mi_corr) * 60))
        manager._notify.debug(
            f"\n\tdate-time as corrected : {corr_y}-{corr_m}-{corr_d} "
            f"{h_corr}:{mi_corr}:{s_corr}",
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
    return jd, corr_y, corr_m, corr_d, h_corr, mi_corr, s_corr
