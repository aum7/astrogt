from typing import Dict
from swe.event import EventEntryData
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SidePaneManager:
    """mixin class for managing the side pane"""

    selected_event = "event_one"
    EVENT_ONE: EventEntryData = None
    EVENT_TWO: EventEntryData = None

    PANE_BUTTONS: Dict[str, str] = {
        "timenow": "time now\nset current time for selected event",
        "settings": "settings",
        "file_save": "save file",
        "file_load": "load file",
    }
    CHANGE_TIME_BUTTONS: Dict[str, str] = {
        "arrow_l_g": "move time backward",
        "arrow_r_g": "move time forward",
        "timenow": "time now\nset current time for selected event",
        "arrow_up_g": "select previous time period",
        "arrow_dn_g": "select next time period",
    }
    # time periods in seconds, used with sweph julian day
    CHANGE_TIME_PERIODS: Dict[str, str] = {
        "period_315360000": "10 years",
        "period_31536000": "1 year",
        "period_7776000": "3 months (90 d)",
        "period_2592000": "1 month (30 d)",
        "period_604800": "1 week",
        "period_86400": "1 day",
        "period_21600": "6 hours",
        "period_3600": "1 hour",
        "period_600": "10 minutes",
        "period_60": "1 minute",
        "period_10": "10 seconds",
        "period_1": "1 second",
    }
    icons_folder: str
    icon_size: Gtk.IconSize
    frm_change_time: Gtk.Frame
    frm_event_one: Gtk.Frame
    frm_event_two: Gtk.Frame

    def init_side_pane(self) -> None:
        """initialize side pane properties"""
        self.icons_pane = "imgs/icons/pane/"
        self.icons_change_time = "imgs/icons/changetime/"
        self.icon_size = Gtk.IconSize.LARGE

    def setup_side_pane(self):
        box_side_pane_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        for button_name, tooltip in self.PANE_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(tooltip)

            icon_name = f"{button_name}.svg"
            # get proper icon
            icon = self.create_pane_icon(icon_name)
            icon.set_icon_size(self.icon_size)
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

            box_side_pane_buttons.append(button)

        # box for all side pane widgets, next to buttons
        box_side_pane_widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # put widgets into main frame
        frm_change_time = self.setup_change_time()
        frm_event_one = self.setup_event("event one")
        frm_event_two = self.setup_event("event two")
        # append to box
        box_side_pane_widgets.append(frm_change_time)
        box_side_pane_widgets.append(frm_event_one)
        box_side_pane_widgets.append(frm_event_two)

        box_side_pane_main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_side_pane_main.append(box_side_pane_buttons)
        box_side_pane_main.append(box_side_pane_widgets)

        return box_side_pane_main

    def create_pane_icon(self, icon_name):
        return Gtk.Image.new_from_file(f"{self.icons_pane}{icon_name}")

    def create_change_time_icon(self, icon_name):
        return Gtk.Image.new_from_file(f"{self.icons_change_time}{icon_name}")

    def setup_change_time(self) -> Gtk.Frame:
        """setup widget for changing time of the event one or two"""
        # main frame of change time widget
        frm_change_time = Gtk.Frame()
        frm_change_time.add_css_class("frame-sidepane")
        # horizontal box for time navigation icons
        box_time_icons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # change time label
        lbl_change_time = Gtk.Label(label="change time :")
        lbl_change_time.add_css_class("label-frame")
        lbl_change_time.set_xalign(0.0)
        lbl_change_time.set_tooltip_text(
            """change time period for selected event (one or two)
hotkeys :
arrow key up / down : select previous / next time period
arrow key left / right : move time backward / forward"""
        )

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
        ddn_time_periods = Gtk.DropDown.new_from_strings(
            self.time_periods_list,
        )
        ddn_time_periods.add_css_class("dropdown")
        # set default time period : 1 day
        default_period = self.time_periods_list.index("1 day")
        ddn_time_periods.set_selected(default_period)
        ddn_time_periods.connect("notify::selected", self.odd_time_period)
        # put label & buttons & dropdown into box
        box_change_time.append(lbl_change_time)
        box_change_time.append(box_time_icons)
        box_change_time.append(ddn_time_periods)

        frm_change_time.set_child(box_change_time)

        return frm_change_time

    def odd_time_period(self, dropdown, *args):
        """on dropdown time period changed / selected"""
        selected = dropdown.get_selected()
        value = self.time_periods_list[selected]
        # print(f"dropdown selected : {value}")
        key = [k for k, v in self.CHANGE_TIME_PERIODS.items() if v == value][0]
        seconds = key.split("_")[-1]
        # print(f"selected period : {seconds} seconds")

    def setup_event(self, event_name: str) -> Gtk.Frame:
        if event_name == "event one":
            # event one datetime & location
            frm_event_one = Gtk.Frame()
            frm_event_one.add_css_class("frame-sidepane")
            # top label : which event
            self.lbl_frm_one = Gtk.Label(label="event one :")
            self.lbl_frm_one.set_tooltip_text(
                """main event ie natal chart
click to set focus to event one
so change time will apply to it"""
            )
            self.lbl_frm_one.set_xalign(0.0)
            # make label clickable
            gesture = Gtk.GestureClick.new()
            gesture.connect(
                "pressed",
                lambda gesture, n_press, x, y: self.obc_event_selection(
                    gesture,
                    n_press,
                    x,
                    y,
                    "event_one",
                ),
            )
            self.lbl_frm_one.add_controller(gesture)
            if self.selected_event == "event_one":
                self.lbl_frm_one.add_css_class("label-frame-sel")
            # next entry for event name
            ent_event_name_one = Gtk.Entry()
            ent_event_name_one.set_placeholder_text("event one name")
            ent_event_name_one.set_tooltip_text(
                "will be used for filename when saving",
            )
            # next below : datetime
            lbl_datetime_one = Gtk.Label(label="date & time")
            lbl_datetime_one.set_halign(Gtk.Align.START)
            # next datetime entry
            ent_datetime_one = Gtk.Entry()
            ent_datetime_one.set_placeholder_text("yyyy MM dd hh mm (ss)")
            ent_datetime_one.set_tooltip_text(
                """ year month day hour minute (second)
    second is optional """
            )
            # next location - label
            lbl_location_one = Gtk.Label(label="location - lat & lon :")
            lbl_location_one.add_css_class("label")
            lbl_location_one.set_halign(Gtk.Align.START)
            # next location entry
            ent_location_one = Gtk.Entry()
            ent_location_one.set_placeholder_text(
                "deg min (sec) n / s deg min (sec) e / w",
            )
            ent_location_one.set_tooltip_text(
                """latitude & longitude
    clearest form is :
        degree minute (second) n(orth) / s(outh) and e(ast) / w(est) 
        34 21 09 n 77 66 w
    will accept also decimal degree : 33.72 n 124.876 e
    and also a sign ('-') for south / west : -16.75 -72.6789
    seconds are optional"""
            )
            # put labels & entries verticaly into a box
            box_event_one = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            # box_datetime_one.set_visible(True)
            box_event_one.append(self.lbl_frm_one)
            box_event_one.append(ent_event_name_one)
            box_event_one.append(lbl_datetime_one)
            box_event_one.append(ent_datetime_one)
            box_event_one.append(lbl_location_one)
            box_event_one.append(ent_location_one)
            # event processing
            self.EVENT_ONE = EventEntryData(
                ent_event_name_one,
                ent_datetime_one,
                ent_location_one,
            )
            # button for current utc
            btn_current_utc = Gtk.Button(label="now")
            btn_current_utc.connect(
                "clicked",
                lambda x: self.EVENT_ONE.set_current_utc(),
            )
            box_event_one.append(btn_current_utc)

            frm_event_one.set_child(box_event_one)

            return frm_event_one

        elif event_name == "event two":
            # event one datetime & location
            frm_event_two = Gtk.Frame()
            frm_event_two.add_css_class("frame-sidepane")
            # top label : which event
            self.lbl_frm_two = Gtk.Label(label="event two :")
            self.lbl_frm_two.set_tooltip_text(
                """secondary event ie transit / progression
click to set focus to event two
so change time will apply to it"""
            )
            self.lbl_frm_two.set_xalign(0.0)
            # make label clickable
            gesture = Gtk.GestureClick.new()
            gesture.connect(
                "pressed",
                lambda gesture, n_pres, x, y: self.obc_event_selection(
                    gesture,
                    n_pres,
                    x,
                    y,
                    "event_two",
                ),
            )
            self.lbl_frm_two.add_controller(gesture)
            self.lbl_frm_two.add_css_class("label-frame")
            # next entry for event name
            ent_event_name_two = Gtk.Entry()
            ent_event_name_two.set_placeholder_text("event two name")
            ent_event_name_two.set_tooltip_text(
                "will be used for filename when saving",
            )
            # next below : datetime
            lbl_datetime_two = Gtk.Label(label="date & time")
            lbl_datetime_two.set_halign(Gtk.Align.START)
            # next datetime entry
            ent_datetime_two = Gtk.Entry()
            ent_datetime_two.set_placeholder_text("yyyy MM dd hh mm (ss)")
            ent_datetime_two.set_tooltip_text(
                """ year month day hour minute (second)
    second is optional """
            )
            # next location - label
            lbl_location_two = Gtk.Label(label="location - lat & lon :")
            lbl_location_two.add_css_class("label")
            lbl_location_two.set_halign(Gtk.Align.START)
            # next location entry
            ent_location_two = Gtk.Entry()
            ent_location_two.set_placeholder_text(
                "deg min (sec) n / s deg min (sec) e / w",
            )
            ent_location_two.set_tooltip_text(
                """latitude & longitude
    clearest form is :
        degree minute (second) n(orth) / s(outh) and e(ast) / w(est) 
        34 21 09 n 77 66 w
    will accept also decimal degree : 33.72 n 124.876 e
    and also a sign ('-') for south / west : -16.75 -72.6789
    seconds are optional"""
            )
            # put labels & entries verticaly into a box
            box_event_two = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            # box_datetime_one.set_visible(True)
            box_event_two.append(self.lbl_frm_two)
            box_event_two.append(ent_event_name_two)
            box_event_two.append(lbl_datetime_two)
            box_event_two.append(ent_datetime_two)
            box_event_two.append(lbl_location_two)
            box_event_two.append(ent_location_two)
            # event processing
            self.EVENT_TWO = EventEntryData(
                ent_event_name_two,
                ent_datetime_two,
                ent_location_two,
            )
            # button for current utc
            btn_current_utc = Gtk.Button(label="now")
            btn_current_utc.connect(
                "clicked",
                lambda x: self.EVENT_TWO.set_current_utc(),
            )
            box_event_two.append(btn_current_utc)

            frm_event_two.set_child(box_event_two)

            return frm_event_two

        else:
            default_frame = Gtk.Frame()
            default_frame.add_css_class("frame-sidepane")

            lbl_error = Gtk.Label(label=f"unknown event : {event_name}")
            lbl_error.add_css_class("label-frame")
            lbl_error.set_xalign(0.0)

            default_frame.set_child(lbl_error)

            return default_frame

    # data handlers
    def get_selected_event_data(self) -> dict:
        """get data for current selected event"""
        if self.selected_event == "event_one":

            return self.EVENT_ONE.get_event_data()

        elif self.selected_event == "event_two":

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
            if self.selected_event == "event_one":
                self.lbl_frm_two.remove_css_class("label-frame-sel")
                self.lbl_frm_two.add_css_class("label-frame")
                self.lbl_frm_one.remove_css_class("label-frame")
                self.lbl_frm_one.add_css_class("label-frame-sel")
            if self.selected_event == "event_two":
                self.lbl_frm_one.remove_css_class("label-frame-sel")
                self.lbl_frm_one.add_css_class("label-frame")
                self.lbl_frm_two.remove_css_class("label-frame")
                self.lbl_frm_two.add_css_class("label-frame-sel")

    def obc_file_save(self, widget, data):
        print(f"{data} clicked")

    def obc_file_load(self, widget, data):
        print(f"{data} clicked")

    # change time funcs
    def obc_arrow_l(self, widget, data):
        print(f"{data} clicked")

    def obc_arrow_r(self, widget, data):
        print(f"{data} clicked")

    def obc_arrow_up(self, widget, data):
        print(f"{data} clicked")

    def obc_arrow_dn(self, widget, data):
        print(f"{data} clicked")
