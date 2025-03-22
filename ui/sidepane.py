# ruff: noqa: E402
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore
from ui.collapsepanel import CollapsePanel
from sweph.eventdata import EventData
from sweph.eventlocation import EventLocation
from sweph.swecore import SweCore
from datetime import datetime, timezone, timedelta
from typing import Dict, Callable, Optional


class SidePaneManager:
    """mixin class for managing the side pane"""

    get_application: Callable[[], Gtk.Application]
    selected_event = "event one"
    EVENT_ONE = None
    EVENT_TWO = None
    swe_core = SweCore()
    margin_end = 7

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

    def setup_side_pane(self):
        # main box for widgets
        box_side_pane_widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_side_pane_widgets.set_size_request(-1, -1)
        # put widgets into box widgets
        self.clp_change_time = self.setup_change_time()
        self.clp_event_one = self.setup_event("event one", True)
        if self.selected_event == "event one":
            self.clp_event_one.add_title_css_class("label-frame-sel")
        self.clp_event_two = self.setup_event("event two", False)
        # tools
        self.clp_tools = self.setup_tools()
        # append to box
        box_side_pane_widgets.append(self.clp_change_time)
        box_side_pane_widgets.append(self.clp_event_one)
        box_side_pane_widgets.append(self.clp_event_two)
        box_side_pane_widgets.append(self.clp_tools)
        # main container scrolled window for collapse panels
        scw_side_pane_widgets = Gtk.ScrolledWindow()
        scw_side_pane_widgets.set_hexpand(False)
        scw_side_pane_widgets.set_propagate_natural_width(True)
        scw_side_pane_widgets.set_child(box_side_pane_widgets)

        return box_side_pane_widgets

    def create_pane_icon(self, icon_name):
        icons_pane = "ui/imgs/icons/pane/"
        return Gtk.Image.new_from_file(f"{icons_pane}{icon_name}")

    def create_change_time_icon(self, icon_name):
        icons_change_time = "ui/imgs/icons/changetime/"
        return Gtk.Image.new_from_file(f"{icons_change_time}{icon_name}")

    def setup_change_time(self) -> CollapsePanel:
        """setup widget for changing time of the event one or two"""
        # main container of change time widget
        clp_change_time = CollapsePanel(title="change time", expanded=False)
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

    def setup_event(self, event_name: str, expand: bool) -> CollapsePanel:
        """setup event one & two collapsible panels, incl location sub-panel"""
        panel = CollapsePanel(
            title="event one" if event_name == "event one" else "event two",
            expanded=expand,
        )
        panel.set_margin_end(self.margin_end)
        lbl_event = panel.get_title()
        lbl_event.set_tooltip_text(
            """main event ie natal / event chart
click to set focus to event one
so change time will apply to it

note : location one + title one
+ time one are mandatory"""
            if event_name == "event one"
            else """secondary event ie transit / progression etc
click to set focus to event two
so change time will apply to it

note : leave location two empty
(both city + latitude & longitude)
if location two = location one"""
        )
        gesture = Gtk.GestureClick.new()
        gesture.connect(
            "pressed",
            lambda gesture, n_press, x, y: self.obc_event_selection(
                gesture, n_press, x, y, event_name
            ),
        )
        panel.add_title_controller(gesture)
        # location nested panel
        subpnl_location = CollapsePanel(
            title="location one" if event_name == "event one" else "location two",
            indent=14,
        )
        lbl_country = Gtk.Label(label="country")
        lbl_country.add_css_class("label")
        lbl_country.set_halign(Gtk.Align.START)

        event_location = EventLocation(self, get_application=self.get_application)
        countries = event_location.get_countries()

        ddn_country = Gtk.DropDown.new_from_strings(countries)
        ddn_country.set_name("country")
        ddn_country.set_tooltip_text(
            """select country for location
in astrogt/user/ folder there is file named
countries.txt
open it with text editor & un-comment any country of interest
    (delete '# ' & save file)
comment (add '# ' & save file) uninterested country"""
        )
        ddn_country.add_css_class("dropdown")
        if event_name == "event one":
            self.country_one = ddn_country
        else:
            self.country_two = ddn_country

        lbl_city = Gtk.Label(label="city")
        lbl_city.add_css_class("label")
        lbl_city.set_halign(Gtk.Align.START)

        ent_city = Gtk.Entry()
        ent_city.set_name("city")

        def update_location(lat, lon, alt):
            ent_location.set_text(f"{lat} {lon} {alt}")

        event_location.set_location_callback(update_location)

        ent_city.set_placeholder_text("enter city name")
        ent_city.set_tooltip_text(
            """enter city name
if more than 1 city (within selected country) is found
user needs to select the one of interest

[enter] = accept data
[tab] / [shift-tab] = next / previous entry"""
        )
        ent_city.connect(
            "activate",
            lambda entry, country: event_location.get_selected_city(entry, country),
            ddn_country,
        )
        if event_name == "event one":
            self.city_one = ent_city
        else:
            self.city_two = ent_city
        # latitude & longitude of event
        lbl_location = Gtk.Label(label="latitude & longitude")
        lbl_location.add_css_class("label")
        lbl_location.set_halign(Gtk.Align.START)

        ent_location = Gtk.Entry()
        ent_location.set_name("location")
        ent_location.set_placeholder_text(
            "deg min (sec) n / s deg  min (sec) e / w",
        )
        ent_location.set_tooltip_text(
            """latitude & longitude

if country & city are filled, this field should be filled auto-magically
user can also enter or fine-tune geo coordinates manually

clearest form is :
    deg min (sec) n(orth) / s(outh) & e(ast) / w(est) (altitude m)
    32 21 09 n 77 66 w 113 m
will accept also decimal degree : 33.72 n 124.876 e
and also a sign ('-') for south & west : -16.75 -72.678
    note : positive values (without '-') are for north & east
        16.75 72.678
seconds & altitude are optional
only use [space] as separator

[enter] = accept data
[tab] / [shift-tab] = next / previous entry"""
        )
        # put widgets into sub-panel
        subpnl_location.add_widget(lbl_country)
        subpnl_location.add_widget(ddn_country)
        subpnl_location.add_widget(lbl_city)
        subpnl_location.add_widget(ent_city)
        subpnl_location.add_widget(lbl_location)
        subpnl_location.add_widget(ent_location)

        subpnl_event_name = CollapsePanel(
            title="name / title one"
            if event_name == "event one"
            else "name / title two",
            indent=14,
        )
        ent_event_name = Gtk.Entry()
        ent_event_name.set_name("event_name")
        ent_event_name.set_placeholder_text(
            "event one name" if event_name == "event one" else "event two name"
        )
        ent_event_name.set_tooltip_text(
            """will be used for filename when saving
    max 30 characters

[enter] = apply data
[tab] / [shift-tab] = next / previous entry"""
        )
        # put widgets into sub-panel
        subpnl_event_name.add_widget(ent_event_name)

        subpnl_datetime = CollapsePanel(
            title="date & time one" if event_name == "event one" else "date & time two",
            indent=14,
        )

        ent_datetime = Gtk.Entry()
        ent_datetime.set_name("date_time")
        ent_datetime.set_placeholder_text("yyyy mm dd HH MM (SS)")
        ent_datetime.set_tooltip_text(
            """year month day hour minute (second)
    2010 9 11 22 55
second is optional
24 hour time format
only use [space] as separator

[enter] = apply & process data
[tab] / [shift-tab] = next / previous entry"""
        )
        ent_datetime.connect(
            "activate",
            lambda widget: self.get_both_events_data(),
        )
        # put widgets into sub-panel
        subpnl_datetime.add_widget(ent_datetime)
        # create eventdata instance
        if event_name == "event one":
            self.EVENT_ONE = EventData(
                ent_event_name,
                ent_datetime,
                ent_location,
                country=ddn_country,
                city=ent_city,
                get_application=self.get_application,
            )
        else:
            self.EVENT_TWO = EventData(
                ent_event_name,
                ent_datetime,
                ent_location,
                country=ddn_country,
                city=ent_city,
                get_application=self.get_application,
            )
        # main box for event panels
        box_event = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # sub-panel
        box_event.append(subpnl_location)
        box_event.append(subpnl_event_name)
        box_event.append(subpnl_datetime)

        panel.add_widget(box_event)

        return panel

    def setup_tools(self) -> CollapsePanel:
        """setup widget for tools buttons, ie save & load file"""
        clp_tools = CollapsePanel(title="tools", expanded=False)
        clp_tools.set_margin_end(self.margin_end)
        clp_tools.set_title_tooltip("""buttons for file load & save etc""")

        box_tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        for button_name, tooltip in self.PANE_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(tooltip)

            icon_name = f"{button_name}.svg"
            # get proper icon
            icon = self.create_pane_icon(icon_name)
            icon.set_icon_size(Gtk.IconSize.NORMAL)
            button.set_child(icon)

            callback_name = f"obc_{button_name}"
            if hasattr(self, callback_name):
                callback = getattr(self, callback_name)
                button.connect("clicked", callback, button_name)
            else:
                button.connect("clicked", self.obc_default, button_name)

            box_tools.append(button)

        clp_tools.add_widget(box_tools)

        return clp_tools

    # todo do we need this & next func ?
    def handle_city_selection(self, entry, country, event_location):
        selected = event_location.get_selected_city(entry, country)
        if selected:
            # update location entry
            location_entry = self.find_location_entry(entry)
            if location_entry:
                lat, lon, alt = [x.strip() for x in selected.split(", ")[1:]]
                location_entry.set_text(f"{lat} {lon} {alt}")

    def find_location_entry(self, ent_city_):
        # find corresponding ent_location in same event panel
        parent = ent_city_.get_parent()
        while parent:
            location_entry = (
                parent.get_child().get_widget("location")
                if hasattr(parent, "get_widget")
                else None
            )
            if location_entry:
                return location_entry
            parent = parent.get_parent()
        return None

    # data handlers
    # todo do we need this ?
    def ensure_event_data(self, event, collapse_panel):
        if isinstance(event, dict):
            return EventData(
                collapse_panel.get_widget("event_name"),
                collapse_panel.get_widget("date_time"),
                collapse_panel.get_widget("location"),
                collapse_panel.get_widget("country"),
                collapse_panel.get_widget("city"),
                get_application=self.get_application,
            )
        # else:
        return EventData(
            collapse_panel.get_widget("event_name"),
            collapse_panel.get_widget("date_time"),
            collapse_panel.get_widget("location"),
            collapse_panel.get_widget("country"),
            collapse_panel.get_widget("city"),
            get_application=self.get_application,
        )
        # return event

    def get_both_events_data(self, widget=None) -> None:
        # self.EVENT_ONE = self.ensure_event_data(self.EVENT_ONE, self.clp_event_one)
        # self.EVENT_TWO = self.ensure_event_data(self.EVENT_TWO, self.clp_event_two)
        event_one_data = self.EVENT_ONE.get_event_data() if self.EVENT_ONE else None
        event_two_data = self.EVENT_TWO.get_event_data() if self.EVENT_TWO else None
        self.swe_core.get_events_data(event_one_data, event_two_data)

    def get_selected_event_data(self, widget=None) -> None:
        """get data for selected event"""
        # print("get_selected_event_data called")
        if self.selected_event == "event one" and self.EVENT_ONE:
            self.swe_core.get_events_data(
                self.EVENT_ONE.get_event_data(),
                None,
            )
        elif self.selected_event == "event two" and self.EVENT_TWO:
            self.swe_core.get_events_data(
                None,
                self.EVENT_TWO.get_event_data(),
            )

    # button handlers
    def event_toggle_selected(self):
        """toggle selected event"""
        if self.selected_event == "event one":
            self.selected_event = "event two"
            print(f"event_toggle_selected : {self.selected_event} selected")
            self.clp_event_one.remove_title_css_class("label-frame-sel")
            self.clp_event_two.add_title_css_class("label-frame-sel")
        elif self.selected_event == "event two":
            self.selected_event = "event one"
            print(f"event_toggle_selected : {self.selected_event} selected")
            self.clp_event_two.remove_title_css_class("label-frame-sel")
            self.clp_event_one.add_title_css_class("label-frame-sel")

    def obc_event_selection(self, gesture, n_press, x, y, event_name):
        """handle event selection"""
        if self.selected_event != event_name:
            self.selected_event = event_name
            if self.selected_event == "event one":
                # todo comment
                print(f"event_selection : {self.selected_event} selected")
                self.clp_event_two.remove_title_css_class("label-frame-sel")
                self.clp_event_one.add_title_css_class("label-frame-sel")
            if self.selected_event == "event two":
                # todo comment
                print(f"event_selection : {self.selected_event} selected")
                self.clp_event_one.remove_title_css_class("label-frame-sel")
                self.clp_event_two.add_title_css_class("label-frame-sel")

    def obc_default(self, widget, data):
        print(f"{data} clicked : obc_default()")

    def obc_settings(self, widget, data):
        # print(f"{data} clicked")
        self.get_application().notify_manager.debug(
            "settings clicked", source="sidepane.py"
        )

    def obc_file_save(self, widget, data):
        print(f"{data} clicked")

    def obc_file_load(self, widget, data):
        print(f"{data} clicked")

    # change time handlers
    def obc_arrow_l(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        self._adjust_event_time(-int(self.CHANGE_TIME_SELECTED))
        self.get_selected_event_data()
        # self.get_application().notify_manager.success(
        #     "time change backward", source="sidepane.py"
        # )

    def obc_arrow_r(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        self._adjust_event_time(int(self.CHANGE_TIME_SELECTED))
        self.get_selected_event_data()
        # self.get_application().notify_manager.success(
        #     "time change forward", source="sidepane.py"
        # )

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
            # self.get_application().notify_manager.info(
            #     f"selected period : {new_value}", source="time change", timeout=5
            # )
            seconds = new_key.split("_")[-1]
            self.CHANGE_TIME_SELECTED = seconds

    def obc_arrow_up(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        """select previous time period"""
        self._change_time_period(direction=-1)
        # self.get_application().notify_manager.info(
        #     "previous time period selected",
        #     source="sidepane.py",
        # )

    def obc_arrow_dn(
        self, widget: Optional[Gtk.Widget] = None, data: Optional[str] = None
    ):
        self._change_time_period(direction=1)
        # self.get_application().notify_manager.info(
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
            self.get_application().notify_manager.warning(
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
                self.get_application().notify_manager.error(
                    "invalid datetime format, using datetime.now utc",
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
