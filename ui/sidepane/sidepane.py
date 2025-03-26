# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Dict, Optional
from ui.collapsepanel import CollapsePanel
from ui.helpers import (
    _on_time_now,
    _process_event,
    _change_event_time,
    _change_time_period,
    _create_icon,
)
from .panelevents import setup_event
from .paneltools import setup_tools
from .panelsettings import setup_settings


class SidePaneManager:
    """mixin class for managing the side pane"""

    CHANGE_TIME_BUTTONS: Dict[str, str] = {
        "arrow_l": "move time backward (hk : arrow left)",
        "arrow_r": "move time forward (hk : arrow right)",
        "time_now": "time now (hk : n)\nset time now for selected ",
        "arrow_up": "select previous time period (hk : arrow up)",
        "arrow_dn": "select next time period (hk : arrow down)",
    }
    # global value for selected change time
    CHANGE_TIME_SELECTED = 0
    # time periods in seconds, used for time change
    # 10 years will vary +- 3 days todo change actual years
    CHANGE_TIME_PERIODS: Dict[str, str] = {
        "period_315360000": "10 years",
        "period_31536000": "1 year",
        "period_7776000": "3 months (90 d)",
        "period_2592000": "1 month (30 d)",
        "period_2360592": "1 month (27.3 d)",
        "period_604800": "1 week",
        "period_86400": "1 day",
        "period_21600": "6 hours",
        "period_3600": "1 hour",
        "period_600": "10 minutes",
        "period_60": "1 minute",
        "period_10": "10 seconds",
        "period_1": "1 second",
    }

    def __init__(self, app=None, *args, **kwargs):
        self._app = app or Gtk.Application.get_default()
        self._notify = self._app.notify_manager
        # initialize attributes
        self.selected_event = "event one"
        self.EVENT_ONE = None
        self.EVENT_TWO = None
        self.margin_end = 7
        # intialize panels
        self.sidepane = self.setup_side_pane()
        self.clp_event_one = None
        self.clp_event_two = None
        self.clp_tools = None
        self.clp_settings = None

    def setup_side_pane(self):
        # main box for widgets
        box_sidepane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # create & put collapse panels into box
        self.clp_change_time = self.setup_change_time()
        # 2 events
        self.clp_event_one = setup_event("event one", True, self)
        if self.selected_event == "event one":
            self.clp_event_one.add_title_css_class("label-event-selected")
        self.clp_event_two = setup_event("event two", False, self)
        # tools
        self.clp_tools = setup_tools(self)
        # settings
        self.clp_settings = setup_settings(self)
        # append to box
        box_sidepane.append(self.clp_change_time)
        box_sidepane.append(self.clp_event_one)
        box_sidepane.append(self.clp_event_two)
        box_sidepane.append(self.clp_tools)
        box_sidepane.append(self.clp_settings)
        # main container scrolled window for collapse panels
        scw_sidepane = Gtk.ScrolledWindow()
        scw_sidepane.set_size_request(-1, -1)
        scw_sidepane.set_hexpand(False)
        scw_sidepane.set_propagate_natural_width(True)
        scw_sidepane.set_child(box_sidepane)

        return scw_sidepane

    def setup_change_time(self) -> CollapsePanel:
        """setup widget for changing time of the event one or two"""
        # main container of change time widget
        clp_change_time = CollapsePanel(title="change time", expanded=True)
        clp_change_time.set_margin_end(self.margin_end)
        clp_change_time.set_title_tooltip(
            """change time period for selected event (one or two)
hotkeys :
arrow key up / down : select previous / next time period
arrow key left / right : move time backward / forward

1 month (27.3 d) = sidereal lunar month"""
        )
        # horizontal box for time navigation icons
        box_time_icons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        for button_name, tooltip in self.CHANGE_TIME_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(tooltip)

            icon = _create_icon(
                self, "ui/imgs/icons/hicolor/scalable/changetime/", f"{button_name}.svg"
            )
            icon.set_icon_size(Gtk.IconSize.NORMAL)

            button.set_child(icon)

            callback_name = f"obc_{button_name}"
            if hasattr(self, callback_name):
                callback = getattr(self, callback_name)
                button.connect(
                    "clicked",
                    callback,
                    button_name,
                )
            else:
                button.connect("clicked", self.obc_default, button_name)

            box_time_icons.append(button)
        # box for icons & dropdown for selecting time period
        box_change_time = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # dropdown time periods list
        self.time_periods_list = list(self.CHANGE_TIME_PERIODS.values())
        # create dropdown
        self.ddn_time_periods = Gtk.DropDown.new_from_strings(self.time_periods_list)
        self.ddn_time_periods.set_tooltip_text(
            "select period to use for time change",
        )
        self.ddn_time_periods.add_css_class("dropdown")
        # set default time period : 1 day & seconds
        default_period = self.time_periods_list.index("1 day")
        self.ddn_time_periods.set_selected(default_period)
        self.CHANGE_TIME_SELECTED = 86400
        self.ddn_time_periods.connect("notify::selected", self.odd_time_period)
        # put label & buttons & dropdown into box
        box_change_time.append(box_time_icons)
        box_change_time.append(self.ddn_time_periods)

        clp_change_time.add_widget(box_change_time)

        return clp_change_time

    def odd_time_period(self, dropdown, user_data=None):
        """on dropdown time period changed / selected"""
        selected = dropdown.get_selected()
        value = self.time_periods_list[selected]
        key = [k for k, v in self.CHANGE_TIME_PERIODS.items() if v == value][0]
        seconds = key.split("_")[-1]
        self.CHANGE_TIME_SELECTED = seconds

    # button handlers
    def obc_default(self, widget, data):
        print(f"{data} clicked : obc_default()")

    def obc_settings(self, widget, data):
        self._notify.debug(f"{data} clicked", source="sidepane")

    def obc_file_save(self, widget, data):
        print(f"{data} clicked")

    def obc_file_load(self, widget, data):
        print(f"{data} clicked")

    # change time handlers
    def obc_arrow_l(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        _change_event_time(self, -int(self.CHANGE_TIME_SELECTED))
        _process_event(self, self.selected_event)
        # self._notify.success(message="time change backward", source="sidepane")

    def obc_arrow_r(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        _change_event_time(self, int(self.CHANGE_TIME_SELECTED))
        _process_event(self, self.selected_event)
        # self._notify.success(message="time change forward", source="sidepane")

    def obc_time_now(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        """set time now for selected event"""
        # obc_time_now needed because button created dynamically
        _on_time_now(self)

    def obc_arrow_up(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        """select previous time period"""
        _change_time_period(self, direction=-1)
        # self._notify.info(
        #     "previous time period selected",
        #     source="sidepane",
        # )

    def obc_arrow_dn(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        _change_time_period(self, direction=1)
        # self._notify.info(
        #     "next time period selected",
        #     source="sidepane",
        # )
