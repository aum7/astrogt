from typing import Dict
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SidePaneManager:
    """mixin class for managing the side pane"""

    selected_event = "event_one"

    PANE_BUTTONS: Dict[str, str] = {
        "event_one": "focus event one",
        "event_two": "focus event two",
        "settings": "settings",
        "file_save": "save file",
        "file_load": "load file",
    }
    CHANGE_TIME_BUTTONS: Dict[str, str] = {
        "arrow_l": "move time backward",
        "arrow_r": "move time forward",
        "arrow_up": "select previous time period",
        "arrow_dn": "select next time period",
    }
    # time periods in seconds, used with sweph julian day
    CHANGE_TIME_PERIODS: Dict[str, str] = {
        "period_315360000": "10 years",
        "period_31536000": "1 year",
        "period_7776000": "3 months (90 days)",
        "period_2592000": "1 month (30 days)",
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
        # ensure init todo do we need init twice ?
        # self.selected_event = "event_one"
        # store references for icon updates
        self.event_buttons = {}

    def get_event_icon(self, button_name: str) -> str:
        """get proper icon for selected event"""
        return (
            f"{button_name}_sel.svg"
            if button_name == self.selected_event
            else f"{button_name}.svg"
        )

    def setup_side_pane(self):
        box_side_pane_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # store reference : todo do we need that ?
        # self.box_side_pane_buttons = box_side_pane_buttons

        for button_name, tooltip in self.PANE_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(tooltip)

            if button_name in ["event_one", "event_two"]:
                icon_name = self.get_event_icon(button_name)
                # store reference for later updates
                self.event_buttons[button_name] = button
            else:
                icon_name = f"{button_name}.svg"
            # get proper icon
            icon = self.create_pane_icon(icon_name)
            icon.set_icon_size(self.icon_size)
            button.set_child(icon)
            # separate handlers
            if button_name in ["event_one", "event_two"]:
                button.connect("clicked", self.obc_event_selection, button_name)
            else:
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
        self.frm_event_one = self.setup_event("event one")
        self.frm_event_two = self.setup_event("event two")
        # append to box
        box_side_pane_widgets.append(frm_change_time)
        box_side_pane_widgets.append(self.frm_event_one)
        box_side_pane_widgets.append(self.frm_event_two)

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
        ddn_time_periods = Gtk.DropDown.new_from_strings(self.time_periods_list)
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
        print(f"dropdown selected : {value}")
        key = [k for k, v in self.CHANGE_TIME_PERIODS.items() if v == value][0]
        seconds = key.split("_")[-1]
        print(f"selected period : {seconds} seconds")

    def setup_event(self, event_name: str) -> Gtk.Frame:
        if event_name == "event one":
            # event one datetime & location
            frm_event_one = Gtk.Frame()
            frm_event_one.add_css_class("frame-sidepane")
            # top label : which event
            lbl_frm_one = Gtk.Label(label="event one :")
            lbl_frm_one.add_css_class("label-frame")
            lbl_frm_one.set_tooltip_text(
                """main event ie natal chart\nclick to set focus to event one"""
            )
            lbl_frm_one.set_xalign(0.0)
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
            box_event_one.append(lbl_frm_one)
            box_event_one.append(lbl_datetime_one)
            box_event_one.append(ent_datetime_one)
            box_event_one.append(lbl_location_one)
            box_event_one.append(ent_location_one)
            frm_event_one.set_child(box_event_one)

            return frm_event_one

        elif event_name == "event two":
            # event one datetime & location
            frm_event_two = Gtk.Frame()
            frm_event_two.add_css_class("frame-sidepane")
            # top label : which event
            lbl_frm_two = Gtk.Label(label="event two :")
            lbl_frm_two.add_css_class("label-frame")
            lbl_frm_two.set_tooltip_text(
                """secondary event ie transit / progression\nclick to set focus to event two"""
            )
            lbl_frm_two.set_xalign(0.0)
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
            box_event_two.append(lbl_frm_two)
            box_event_two.append(lbl_datetime_two)
            box_event_two.append(ent_datetime_two)
            box_event_two.append(lbl_location_two)
            box_event_two.append(ent_location_two)
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

    # button handlers
    def obc_default(self, widget, data):
        print(f"{data} clicked : obc_default()")

    def obc_settings(self, widget, data):
        print(f"{data} clicked")

    def obc_event_selection(self, widget, event_name):
        """handle event selection"""
        # print(f"widget : {widget}")
        if self.selected_event != event_name:
            self.selected_event = event_name
            if self.selected_event == "event_one":
                print("selected EVENT ONE")
                self.frm_event_two.remove_css_class("label-frame-sel")
                self.frm_event_one.remove_css_class("label-frame")
                self.frm_event_one.add_css_class("label-frame-sel")
            if self.selected_event == "event_two":
                print("selected EVENT TWO")
                self.frm_event_one.remove_css_class("label-frame-sel")
                self.frm_event_two.remove_css_class("label-frame")
                self.frm_event_two.add_css_class("label-frame-sel")
            # update icons
            # for btn_name in ["event_one", "event_two"]:
            #     button = self.event_buttons.get(btn_name)
            #     if button:
            #         icon_name = self.get_event_icon(btn_name)
            #         new_icon = self.create_pane_icon(icon_name)
            #         new_icon.set_icon_size(self.icon_size)
            #         # old_icon = button.get_child()
            #         # if old_icon:
            #         #     button.remove(old_icon)
            #         button.set_child(new_icon)
            # break
        print(f"selected event changed : {event_name}")

    # def obc_event_one(self, widget, data):
    #     if self.selected_event != "event_one":
    #         self.selected_event = "event_one"
    #     self.update_event_buttons()
    #     print(f"{data} clicked - selected : {self.selected_event}")

    # def obc_event_two(self, widget, data):
    #     if self.selected_event != "event_one":
    #         self.selected_event = "event_one"
    #     self.update_event_buttons()
    #     print(f"{data} clicked - selected : {self.selected_event}")

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
