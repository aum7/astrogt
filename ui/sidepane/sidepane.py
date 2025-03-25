# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from ui.collapsepanel import CollapsePanel
from .panelevents import (
    setup_event,
    get_selected_event_data,
    # event_toggle_selected,
    # obc_event_selection,
)
from .paneltools import setup_tools
from .panelsettings import setup_settings


class SidePaneManager:
    """mixin class for managing the side pane"""

    PANE_BUTTONS: Dict[str, str] = {
        "settings": "settings",
        "file_save": "save file",
        "file_load": "load file",
    }
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

    def event_toggle_selected(self):
        """toggle selected event"""
        if self.selected_event == "event one":
            self.selected_event = "event two"
            print(f"event_toggle_selected : {self.selected_event} selected")
            if self.clp_event_one:
                self.clp_event_one.remove_title_css_class("label-event-selected")
            if self.clp_event_two:
                self.clp_event_two.add_title_css_class("label-event-selected")
        elif self.selected_event == "event two":
            self.selected_event = "event one"
            print(f"event_toggle_selected : {self.selected_event} selected")
            if self.clp_event_two:
                self.clp_event_two.remove_title_css_class("label-event-selected")
            if self.clp_event_one:
                self.clp_event_one.add_title_css_class("label-event-selected")

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

    def create_pane_icon(self, icon_name):
        icons_pane = "ui/imgs/icons/pane/"
        return Gtk.Image.new_from_file(f"{icons_pane}{icon_name}")

    def create_change_time_icon(self, icon_name):
        icons_change_time = "ui/imgs/icons/changetime/"
        return Gtk.Image.new_from_file(f"{icons_change_time}{icon_name}")

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

            icon = self.create_change_time_icon(f"{button_name}.svg")
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

    # todo do we need this & next func ?
    # def handle_city_selection(self, entry, country, event_location):
    #     selected = event_location.get_selected_city(entry, country)
    #     if selected:
    #         # update location entry
    #         location_entry = self.find_location_entry(entry)
    #         if location_entry:
    #             lat, lon, alt = [x.strip() for x in selected.split(", ")[1:]]
    #             location_entry.set_text(f"{lat} {lon} {alt}")

    # def find_location_entry(self, ent_city_):
    #     # find corresponding ent_location in same event panel
    #     parent = ent_city_.get_parent()
    #     while parent:
    #         location_entry = (
    #             parent.get_child().get_widget("location")
    #             if hasattr(parent, "get_widget")
    #             else None
    #         )
    #         if location_entry:
    #             return location_entry
    #         parent = parent.get_parent()
    #     return None

    # button handlers

    def obc_default(self, widget, data):
        print(f"{data} clicked : obc_default()")

    def obc_settings(self, widget, data):
        self._notify.debug(f"{data} clicked", source="sidepane.py")

    def obc_file_save(self, widget, data):
        print(f"{data} clicked")

    def obc_file_load(self, widget, data):
        print(f"{data} clicked")

    # change time handlers
    def obc_arrow_l(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        self._adjust_event_time(-int(self.CHANGE_TIME_SELECTED))
        get_selected_event_data(self)
        # self._notify.success(message="time change backward", source="sidepane.py")

    def obc_arrow_r(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        self._adjust_event_time(int(self.CHANGE_TIME_SELECTED))
        get_selected_event_data(self)
        # self._notify.success(message="time change forward", source="sidepane.py")

    def obc_time_now(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        """set time now for selected event"""
        if self.selected_event == "event one" and self.EVENT_ONE:
            self.EVENT_ONE.set_current_utc()
        elif self.selected_event == "event two" and self.EVENT_TWO:
            self.EVENT_TWO.set_current_utc()

    def _change_time_period(
        self,
        widget: Optional[Gtk.Widget] = None,
        data: Optional[str] = None,
        direction=1,
    ):
        """helper function to change time period ; direction -1 / 1 for previous / next"""
        # get list of periods
        period_keys = list(self.CHANGE_TIME_PERIODS.keys())
        period_values = list(self.CHANGE_TIME_PERIODS.values())
        # get current selected
        current_value = self.time_periods_list[self.ddn_time_periods.get_selected()]
        current_key = next(
            (k for k, v in self.CHANGE_TIME_PERIODS.items() if v == current_value), None
        )
        if current_key:
            current_index = period_keys.index(current_key)
            new_index = (current_index + direction) % len(period_keys)
            new_key = period_keys[new_index]
            new_value = self.CHANGE_TIME_PERIODS[new_key]
            # set new value
            dropdown_index = period_values.index(new_value)
            self.ddn_time_periods.set_selected(dropdown_index)
            # notify new value
            # self._notify.info(
            #     f"selected period : {new_value}", source="time change", timeout=3
            # )
            seconds = new_key.split("_")[-1]
            self.CHANGE_TIME_SELECTED = seconds

    def obc_arrow_up(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        """select previous time period"""
        self._change_time_period(direction=-1)
        # self._notify.info(
        #     "previous time period selected",
        #     source="sidepane.py",
        # )

    def obc_arrow_dn(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        self._change_time_period(direction=1)
        # self._notify.info(
        #     "next time period selected",
        #     source="sidepane.py",
        # )

    def _adjust_event_time(self, sec_delta):
        """adjust event time by given seconds"""
        # get active entry : event one or two
        entry = self._get_active_ent_datetime()
        if not entry:
            return
        # get current datetime
        current_text = entry.get_text().strip()
        # if empty, use current utc
        if not current_text:
            self._notify.warning(
                "datetime None", source="sidepane.py [adjust_event_time]"
            )
            current_utc = datetime.now(timezone.utc)
        else:
            try:
                # parse datetime
                current_utc = datetime.strptime(current_text, "%Y-%m-%d %H:%M:%S")
                # assume utc todo
                current_utc = current_utc.replace(tzinfo=timezone.utc)
            except ValueError:
                self._notify.error(
                    "adjusteventtime : invalid datetime format, using datetime.now utc",
                    source="sidepane.py",
                )
                current_utc = datetime.now(timezone.utc)
        # apply delta
        current_utc = current_utc + timedelta(seconds=int(sec_delta))
        # format & set new value
        new_text = current_utc.strftime("%Y-%m-%d %H:%M:%S")
        entry.set_text(new_text)
        # trigger entry activate signal
        entry.activate()

    def _get_active_ent_datetime(self):
        """get datetime entry for selected / active event"""
        if self.selected_event == "event one" and self.EVENT_ONE:
            return self.EVENT_ONE.date_time
        elif self.selected_event == "event two" and self.EVENT_TWO:
            return self.EVENT_TWO.date_time
        return None
