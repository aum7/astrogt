from typing import Dict
from swe.event import EventEntryData
from ui.collapsepanel import CollapsePanel
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SidePaneManager:
    """mixin class for managing the side pane"""

    selected_event = "event one"
    EVENT_ONE: EventEntryData = None
    EVENT_TWO: EventEntryData = None

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
        box_side_pane_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

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

            box_side_pane_buttons.append(button)

        # main box for widgets
        box_side_pane_widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # put widgets into main frame
        clp_change_time = self.setup_change_time()
        self.clp_event_one = self.setup_event("event one")
        if self.selected_event == "event one":
            self.clp_event_one.add_title_css_class("label-frame-sel")
        self.clp_event_two = self.setup_event("event two")
        # append to box
        box_side_pane_widgets.append(clp_change_time)
        box_side_pane_widgets.append(self.clp_event_one)
        box_side_pane_widgets.append(self.clp_event_two)
        # side pane main box
        box_side_pane_main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_side_pane_main.append(box_side_pane_buttons)
        box_side_pane_main.append(box_side_pane_widgets)
        # main container scrolled window
        scw_pane_widgets = Gtk.ScrolledWindow()
        scw_pane_widgets.set_child(box_side_pane_main)
        scw_pane_widgets.set_hexpand(True)
        scw_pane_widgets.set_visible(True)

        return scw_pane_widgets
        # return box_side_pane_main

    def create_pane_icon(self, icon_name):
        icons_pane = "imgs/icons/pane/"
        return Gtk.Image.new_from_file(f"{icons_pane}{icon_name}")

    def create_change_time_icon(self, icon_name):
        icons_change_time = "imgs/icons/changetime/"
        return Gtk.Image.new_from_file(f"{icons_change_time}{icon_name}")

    def setup_change_time(self) -> CollapsePanel:
        """setup widget for changing time of the event one or two"""
        # main container of change time widget
        clp_change_time = CollapsePanel(title="change time", expanded=False)
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
                    lambda btn, name=button_name: callback(btn, name),
                )
            else:
                button.connect("clicked", self.obc_default, button_name)
            box_time_icons.append(button)

        # box for icons & dropdown for selecting time period
        box_change_time = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # dropdown time periods list
        self.time_periods_list = list(self.CHANGE_TIME_PERIODS.values())
        # create dropdown
        ddn_time_periods = Gtk.DropDown.new_from_strings(self.time_periods_list)
        ddn_time_periods.add_css_class("dropdown")
        # set default time period : 1 day
        default_period = self.time_periods_list.index("1 day")
        ddn_time_periods.set_selected(default_period)
        ddn_time_periods.connect("notify::selected", self.odd_time_period)
        # put label & buttons & dropdown into box
        # box_change_time.append(lbl_change_time)
        box_change_time.append(box_time_icons)
        box_change_time.append(ddn_time_periods)

        clp_change_time.add_widget(box_change_time)

        return clp_change_time

    def odd_time_period(self, dropdown, *args):
        """on dropdown time period changed / selected"""
        selected = dropdown.get_selected()
        value = self.time_periods_list[selected]
        # print(f"dropdown selected : {value}")
        key = [k for k, v in self.CHANGE_TIME_PERIODS.items() if v == value][0]
        seconds = key.split("_")[-1]
        # print(f"selected period : {seconds} seconds")
        self.CHANGE_TIME_SELECTED = seconds

    def setup_event(self, event_name: str) -> CollapsePanel:
        panel = CollapsePanel(
            title="event one" if event_name == "event one" else "event two",
            expanded=False,
        )
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
only use space as separator

[enter] = apply data
[tab] / [shift-tab] = next / previous entry"""
        )
        lbl_location = Gtk.Label(label="location")
        lbl_location.add_css_class("label")
        lbl_location.set_halign(Gtk.Align.START)

        ent_location = Gtk.Entry()
        ent_location.set_placeholder_text("deg min (sec) n / s deg  min (sec) e / w")
        ent_location.set_tooltip_text(
            """latitude & longitude

clearest form is :
    deg min (sec) n(orth) / s(outh) & e(ast) / w(est)
    32 21 09 n 77 66 w
will accept also decimal degree : 33.72 n 124.876 e
and also a sign ('-') for south & west : -16.75 -72.678
seconds are optional
only use space as separator

[enter] = accept data
[tab] / [shift-tab] = next / previous entry"""
        )
        box_event = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_event.append(ent_event_name)
        box_event.append(lbl_datetime)
        box_event.append(ent_datetime)
        box_event.append(lbl_location)
        box_event.append(ent_location)

        if event_name == "event one":
            self.EVENT_ONE = EventEntryData(
                ent_event_name,
                ent_datetime,
                ent_location,
            )
        else:
            self.EVENT_TWO = EventEntryData(
                ent_event_name,
                ent_datetime,
                ent_location,
            )

        panel.add_widget(box_event)

        return panel

    #         if event_name == "event one":
    #             # create collapse panel
    #             self.clp_event_one = CollapsePanel(title="event one")
    #             # top label : which event
    #             self.clp_event_one.set_title_tooltip(
    #                 """main event ie natal chart
    # click to set focus to event one
    # so change time will apply to it"""
    #             )
    #             # make label clickable
    #             gesture = Gtk.GestureClick.new()
    #             gesture.connect(
    #                 "pressed",
    #                 lambda gesture, n_press, x, y: self.obc_event_selection(
    #                     gesture,
    #                     n_press,
    #                     x,
    #                     y,
    #                     "event_one",
    #                 ),
    #             )
    #             self.clp_event_one.add_title_controller(gesture)
    #             self.clp_event_one.add_title_css_class("label-frame-sel")
    #             # next entry for event name
    #             ent_event_name_one = Gtk.Entry()
    #             ent_event_name_one.set_placeholder_text("event one name")
    #             ent_event_name_one.set_tooltip_text(
    #                 """ will be used for filename when saving
    #     max 30 characters

    # [enter] = apply data
    # [tab] / [shift-tab] = next / previous entry """
    #             )
    #             # next below : datetime
    #             lbl_datetime_one = Gtk.Label(label="date & time")
    #             lbl_datetime_one.set_halign(Gtk.Align.START)
    #             # next datetime entry
    #             ent_datetime_one = Gtk.Entry()
    #             ent_datetime_one.set_placeholder_text("yyyy mm dd HH MM (SS)")
    #             ent_datetime_one.set_tooltip_text(
    #                 """year month day hour minute (second)
    #     2010 9 11 22 55
    # second is optional
    # 24 hour time format
    # only use space as separator

    # [enter] = apply data
    # [tab] / [shift-tab] = focus next / previous entry"""
    #             )
    #             # next location - label
    #             lbl_location_one = Gtk.Label(label="location - lat & lon :")
    #             lbl_location_one.add_css_class("label")
    #             lbl_location_one.set_halign(Gtk.Align.START)
    #             # next location entry
    #             ent_location_one = Gtk.Entry()
    #             ent_location_one.set_placeholder_text(
    #                 "deg min (sec) n / s deg min (sec) e / w",
    #             )
    #             ent_location_one.set_tooltip_text(
    #                 """latitude & longitude

    # clearest form is :
    #     deg min (sec) n(orth) / s(outh) & e(ast) / w(est)
    #     34 21 09 n 77 66 w
    # will accept also decimal degree : 33.72 n 124.876 e
    # and also a sign ('-') for south & west : -16.75 -72.6789
    # seconds are optional
    # only use space as separator

    # [enter] = apply data
    # [tab] / [shift-tab] = focus next / previous entry"""
    #             )
    #             # put labels & entries verticaly into a box
    #             box_event_one = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    #             box_event_one.append(ent_event_name_one)
    #             box_event_one.append(lbl_datetime_one)
    #             box_event_one.append(ent_datetime_one)
    #             box_event_one.append(lbl_location_one)
    #             box_event_one.append(ent_location_one)
    #             # event processing
    #             self.EVENT_ONE = EventEntryData(
    #                 ent_event_name_one,
    #                 ent_datetime_one,
    #                 ent_location_one,
    #             )
    #             self.clp_event_one.add_widget(box_event_one)
    #             # frm_event_one.set_child(box_event_one)

    #             return self.clp_event_one
    #             # return frm_event_one

    #         elif event_name == "event two":
    #             # event one datetime & location
    #             # create collapse panel
    #             self.clp_event_two = CollapsePanel(title="event two", expanded=False)
    #             # top label : which event
    #             self.clp_event_two.set_title_tooltip(
    #                 """secondary event ie transit / progression
    # click to set focus to event two
    # so change time will apply to it"""
    #             )
    #             # make label clickable
    #             gesture = Gtk.GestureClick.new()
    #             gesture.connect(
    #                 "pressed",
    #                 lambda gesture, n_pres, x, y: self.obc_event_selection(
    #                     gesture,
    #                     n_pres,
    #                     x,
    #                     y,
    #                     "event_two",
    #                 ),
    #             )
    #             self.clp_event_two.add_title_controller(gesture)
    #             self.clp_event_two.add_title_css_class("label-frame")
    #             # next entry for event name
    #             ent_event_name_two = Gtk.Entry()
    #             ent_event_name_two.set_placeholder_text("event two name")
    #             ent_event_name_two.set_tooltip_text(
    #                 """will be used for filename when saving

    # [enter] = apply data
    # [tab] / [shift-tab] = next / previous entry """
    #             )
    #             # next below : datetime
    #             lbl_datetime_two = Gtk.Label(label="date & time")
    #             lbl_datetime_two.set_halign(Gtk.Align.START)
    #             # next datetime entry
    #             ent_datetime_two = Gtk.Entry()
    #             ent_datetime_two.set_placeholder_text("yyyy MM dd hh mm (ss)")
    #             ent_datetime_two.set_tooltip_text(
    #                 """year month day hour minute (second)
    #     2010 9 11 22 55
    # second is optional
    # 24 hour time format
    # only use space as separator

    # [enter] = apply data
    # [tab] / [shift-tab] = focus next / previous entry"""
    #             )
    #             # next location - label
    #             lbl_location_two = Gtk.Label(label="location - lat & lon :")
    #             lbl_location_two.add_css_class("label")
    #             lbl_location_two.set_halign(Gtk.Align.START)
    #             # next location entry
    #             ent_location_two = Gtk.Entry()
    #             ent_location_two.set_placeholder_text(
    #                 "deg min (sec) n / s deg min (sec) e / w",
    #             )
    #             ent_location_two.set_tooltip_text(
    #                 """latitude & longitude
    #
    # clearest form is :
    #     degree minute (second) n(orth) / s(outh) & e(ast) / w(est)
    #     34 21 09 n 77 66 w
    # will accept also decimal degree : 33.72 n 124.876 e
    # and also a sign ('-') for south & west : -16.75 -72.6789
    # seconds are optional
    # only use space as separator

    # [enter] = apply data
    # [tab] / [shift-tab] = focus next / previous entry"""
    #             )
    #             # put labels & entries verticaly into a box
    #             box_event_two = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    #             # box_datetime_one.set_visible(True)
    #             box_event_two.append(ent_event_name_two)
    #             box_event_two.append(lbl_datetime_two)
    #             box_event_two.append(ent_datetime_two)
    #             box_event_two.append(lbl_location_two)
    #             box_event_two.append(ent_location_two)
    #             # event processing
    #             self.EVENT_TWO = EventEntryData(
    #                 ent_event_name_two,
    #                 ent_datetime_two,
    #                 ent_location_two,
    #             )
    #             self.clp_event_two.add_widget(box_event_two)

    #             return self.clp_event_two

    #         else:
    #             clp_default = CollapsePanel()
    #             clp_default.set_title("error : unknown event")

    #             return clp_default

    # data handlers
    def get_selected_event_data(self) -> dict:
        """get data for current selected event"""
        if self.selected_event == "event one":

            return self.EVENT_ONE.get_event_data()

        elif self.selected_event == "event two":

            return self.EVENT_TWO.get_event_data()

        return {}

    def get_both_events_data(self) -> tuple:
        """get data for both events"""
        event_one = self.EVENT_ONE.get_event_data() if self.EVENT_ONE else None
        event_two = self.EVENT_TWO.get_event_data() if self.EVENT_TWO else None
        return (event_one, event_two)

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
                self.clp_event_two.remove_title_css_class("label-frame-sel")
                self.clp_event_two.add_title_css_class("label-frame")
                self.clp_event_one.remove_title_css_class("label-frame")
                self.clp_event_one.add_title_css_class("label-frame-sel")
            if self.selected_event == "event two":
                self.clp_event_one.remove_title_css_class("label-frame-sel")
                self.clp_event_one.add_title_css_class("label-frame")
                self.clp_event_two.remove_title_css_class("label-frame")
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
        print(f"{data} clicked")
        if self.selected_event == "event one" and self.EVENT_ONE:
            self.EVENT_ONE.set_current_utc()
        elif self.selected_event == "event two" and self.EVENT_TWO:
            self.EVENT_TWO.set_current_utc()

    def obc_arrow_up_g(self, widget, data):
        print(f"{data} clicked")

    def obc_arrow_dn_g(self, widget, data):
        print(f"{data} clicked")
