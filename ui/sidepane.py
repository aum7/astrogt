# ruff: noqa: E402
from typing import Dict
from ui.collapsepanel import CollapsePanel
from swe.eventdata import EventData
from swe.eventlocation import EventLocation
from swe.swecore import SweCore
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SidePaneManager:
    """mixin class for managing the side pane"""

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
        "arrow_l_g": "move time backward",
        "arrow_r_g": "move time forward",
        "time_now": "time now\nset time now for selected location",
        "arrow_up_g": "select previous time period",
        "arrow_dn_g": "select next time period",
    }
    # global value for selected change time
    CHANGE_TIME_SELECTED = 0
    # time periods in seconds, used with sweph julian day
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
        # box_side_pane_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # for button_name, tooltip in self.PANE_BUTTONS.items():
        #     button = Gtk.Button()
        #     button.add_css_class("button-pane")
        #     button.set_tooltip_text(tooltip)

        #     icon_name = f"{button_name}.svg"
        #     # get proper icon
        #     icon = self.create_pane_icon(icon_name)
        #     icon.set_icon_size(Gtk.IconSize.NORMAL)
        #     button.set_child(icon)

        #     callback_name = f"obc_{button_name}"
        #     if hasattr(self, callback_name):
        #         callback = getattr(self, callback_name)
        #         button.connect("clicked", callback, button_name)
        #     else:
        #         button.connect("clicked", self.obc_default, button_name)

        #     box_side_pane_buttons.append(button)

        # main box for widgets
        box_side_pane_widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_side_pane_widgets.set_size_request(-1, -1)
        # put widgets into box widgets
        clp_change_time = self.setup_change_time()
        self.clp_event_one = self.setup_event("event one", True)
        if self.selected_event == "event one":
            self.clp_event_one.add_title_css_class("label-frame-sel")
        self.clp_event_two = self.setup_event("event two", False)
        # tools
        self.clp_tools = self.setup_tools()
        # append to box
        box_side_pane_widgets.append(clp_change_time)
        box_side_pane_widgets.append(self.clp_event_one)
        box_side_pane_widgets.append(self.clp_event_two)
        box_side_pane_widgets.append(self.clp_tools)
        # main container scrolled window for collapse panels
        scw_side_pane_widgets = Gtk.ScrolledWindow()
        scw_side_pane_widgets.set_hexpand(False)
        scw_side_pane_widgets.set_propagate_natural_width(True)
        scw_side_pane_widgets.set_child(box_side_pane_widgets)
        # side pane main box
        # box_side_pane_main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # box_side_pane_main.set_size_request(-1, -1)
        # box_side_pane_main.append(box_side_pane_buttons)
        # box_side_pane_main.append(scw_side_pane_widgets)

        return box_side_pane_widgets
        # return box_side_pane_main

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
        ddn_time_periods = Gtk.DropDown.new_from_strings(
            self.time_periods_list,
        )
        ddn_time_periods.set_tooltip_text(
            "select period to use for time change",
        )
        ddn_time_periods.add_css_class("dropdown")
        # set default time period : 1 day
        default_period = self.time_periods_list.index("1 day")
        ddn_time_periods.set_selected(default_period)
        ddn_time_periods.connect("notify::selected", self.odd_time_period)
        # put label & buttons & dropdown into box
        box_change_time.append(box_time_icons)
        box_change_time.append(ddn_time_periods)

        clp_change_time.add_widget(box_change_time)

        return clp_change_time

    def odd_time_period(self, dropdown):
        """on dropdown time period changed / selected"""
        selected = dropdown.get_selected()
        value = self.time_periods_list[selected]
        # print(f"dropdown selected : {value}")
        key = [k for k, v in self.CHANGE_TIME_PERIODS.items() if v == value][0]
        seconds = key.split("_")[-1]
        # print(f"selected period : {seconds} seconds")
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
            """main event ie natal chart
click to set focus to event one
so change time will apply to it"""
            if event_name == "event one"
            else """secondary event ie transit / progression
click to set focus to event two
so change time will apply to it"""
        )
        gesture = Gtk.GestureClick.new()
        gesture.connect(
            "pressed",
            lambda gesture, n_press, x, y: self.obc_event_selection(
                gesture, n_press, x, y, event_name
            ),
        )
        panel.add_title_controller(gesture)

        ent_event_name = Gtk.Entry()
        ent_event_name.set_placeholder_text(
            "event one name" if event_name == "event one" else "event two name"
        )
        ent_event_name.set_tooltip_text(
            """will be used for filename when saving
    max 30 characters

[enter] = apply data
[tab] / [shift-tab] = next / previous entry"""
        )
        lbl_datetime = Gtk.Label(label="date & time")
        lbl_datetime.set_halign(Gtk.Align.START)

        ent_datetime = Gtk.Entry()
        ent_datetime.set_placeholder_text("yyyy mm dd HH MM (SS)")
        ent_datetime.set_tooltip_text(
            """year month day hour minute (second)
    2010 9 11 22 55
second is optional
24 hour time format
only use [space] as separator

[enter] = apply data
[tab] / [shift-tab] = next / previous entry"""
        )
        # location nested panel
        sub_panel = CollapsePanel(
            title="location one" if event_name == "event one" else "location two",
            indent=14,
        )
        lbl_country = Gtk.Label(label="country")
        lbl_country.add_css_class("label")
        lbl_country.set_halign(Gtk.Align.START)

        event_location = EventLocation(self)
        countries = event_location.get_countries()

        ddn_country = Gtk.DropDown.new_from_strings(countries)
        ddn_country.set_tooltip_text(
            """select country for location
in astrogt/user/ folder there is file named
countries.txt
open it with text editor & un-comment any country of interest
    (delete '# ' & save file)
comment (add '# ' & save file) uninterested country"""
        )
        ddn_country.add_css_class("dropdown")

        lbl_city = Gtk.Label(label="city")
        lbl_city.add_css_class("label")
        lbl_city.set_halign(Gtk.Align.START)

        ent_city = Gtk.Entry()

        def update_location(lat, lon, alt):
            ent_location.set_text(f"{lat} {lon} {alt}")

        event_location.set_location_callback(update_location)

        ent_city.set_placeholder_text("enter city name")
        ent_city.set_tooltip_text(
            """type city name & confirm with [enter]
if more than 1 city (within selected country) is found
user needs to select the one of interest"""
        )
        ent_city.connect(
            "activate",
            lambda entry, country: event_location.get_selected_city(entry, country),
            ddn_country,
        )
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

[enter] = accept & process data
[tab] / [shift-tab] = next / previous entry"""
        )
        ent_location.connect(
            "activate",
            lambda widget: self.get_both_events_data(),
        )
        # put widgets into sub-panel
        sub_panel.add_widget(lbl_country)
        sub_panel.add_widget(ddn_country)
        sub_panel.add_widget(lbl_city)
        sub_panel.add_widget(ent_city)
        sub_panel.add_widget(lbl_location)
        sub_panel.add_widget(ent_location)

        # create eventdata instance
        # event_data = EventData(ent_event_name, ent_datetime, ent_location)
        if event_name == "event one":
            self.EVENT_ONE = EventData(
                ent_event_name,
                ent_datetime,
                ent_location,
            )
        else:
            self.EVENT_TWO = EventData(
                ent_event_name,
                ent_datetime,
                ent_location,
            )
        # main box for event panels
        box_event = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_event.append(ent_event_name)
        box_event.append(lbl_datetime)
        box_event.append(ent_datetime)
        # sub-panel
        box_event.append(sub_panel)

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
    # def get_selected_event_data(self) -> None:
    #     """get data for current selected event"""
    #     print("get_selected_event_data called")
    #     if self.selected_event == "event one" and self.EVENT_ONE:
    #         self.swe_core.get_events_data(
    #             self.EVENT_ONE.get_event_data(),
    #             None,
    #         )

    #     elif self.selected_event == "event two" and self.EVENT_TWO:
    #         self.swe_core.get_events_data(
    #             None,
    #             self.EVENT_TWO.get_event_data(),
    #         )

    # return {}

    def get_both_events_data(self, widget=None) -> None:
        """get data for both events"""
        try:
            event_one = (
                self.EVENT_ONE.get_event_data()
                if isinstance(self.EVENT_ONE, EventData)
                else None
            )
            event_two = (
                self.EVENT_TWO.get_event_data()
                if isinstance(self.EVENT_TWO, EventData)
                else None
            )
            self.swe_core.get_events_data(self, event_one, event_two)

        except AttributeError:
            # re-initialize if they be converted to dict
            if isinstance(self.EVENT_ONE, dict):
                self.EVENT_ONE = EventData(
                    self.clp_event_one.get_widget("event_name"),
                    self.clp_event_one.get_widget("date_time"),
                    self.clp_event_one.get_widget("location"),
                )
            if isinstance(self.EVENT_TWO, dict):
                self.EVENT_TWO = EventData(
                    self.clp_event_two.get_widget("event_name"),
                    self.clp_event_two.get_widget("date_time"),
                    self.clp_event_two.get_widget("location"),
                )
            # try again
            event_one = (
                self.EVENT_ONE.get_event_data()
                if isinstance(self.EVENT_ONE, EventData)
                else None
            )
            event_two = (
                self.EVENT_TWO.get_event_data()
                if isinstance(self.EVENT_TWO, EventData)
                else None
            )
            self.swe_core.get_events_data(self, event_one, event_two)
        # return (event_one, event_two)

    # button handlers
    def obc_default(self, widget, data):
        print(f"{data} clicked : obc_default()")

    def obc_settings(self, widget, data):
        print(f"{data} clicked")

    def obc_event_selection(self, gesture, n_press, x, y, event_name):
        """handle event selection"""
        if self.selected_event != event_name:
            self.selected_event = event_name
            if self.selected_event == "event one":
                print("event_selection : event one selected")
                self.clp_event_two.remove_title_css_class("label-frame-sel")
                self.clp_event_one.add_title_css_class("label-frame-sel")
            if self.selected_event == "event two":
                print("event_selection : event two selected")
                self.clp_event_one.remove_title_css_class("label-frame-sel")
                self.clp_event_two.add_title_css_class("label-frame-sel")

    def obc_file_save(self, widget, data):
        print(f"{data} clicked")

    def obc_file_load(self, widget, data):
        print(f"{data} clicked")

    # change time funcs
    def obc_arrow_l_g(self, widget, data):
        print(f"{data} clicked")

    def obc_arrow_r_g(self, widget, data):
        print(f"{data} clicked")

    def obc_time_now(self, widget, data):
        """set time now for selected event"""
        if self.selected_event == "event one" and self.EVENT_ONE:
            self.EVENT_ONE.set_current_utc()
        elif self.selected_event == "event two" and self.EVENT_TWO:
            self.EVENT_TWO.set_current_utc()

    def obc_arrow_up_g(self, widget, data):
        print(f"{data} clicked")

    def obc_arrow_dn_g(self, widget, data):
        print(f"{data} clicked")
