from typing import Dict, Any

# import os
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # type: ignore


class SidePaneManager:
    """mixin class for managing the side pane
    note: this class is intended to be used with gtk.applicationwindow
    and should not be instantiated directly
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """ensure proper mixin init"""
        super().__init_subclass__(**kwargs)

    PANE_BUTTONS: Dict[str, str] = {
        "settings": "settings",
        "event_one": "data & focus to event 1",
        "event_two": "data & focus to event 2",
        "file_save": "save file",
        "file_load": "load file",
    }
    icons_folder: str
    icons_list: list[str]
    icon_size: Gtk.IconSize

    def init_side_pane(self) -> None:
        """initialize side pane properties"""
        self.icons_folder = "imgs/icons/pane/"
        self.icon_size = Gtk.IconSize.LARGE

    def setup_side_pane(self):
        box_side_pane_buttons = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_side_pane_buttons.set_visible(True)

        for button_name, tooltip in self.PANE_BUTTONS.items():
            button = Gtk.Button()
            button.add_css_class("button-pane")
            button.set_tooltip_text(tooltip)

            icon = self.create_pane_icon(f"{button_name}.svg")
            icon.set_icon_size(self.icon_size)
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

            box_side_pane_buttons.append(button)

        box_side_pane_widgets = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # box_side_pane_widgets.set_visible(True)
        # box_side_pane_widgets.set_hexpand(True)
        # box_side_pane_widgets.set_vexpand(True)
        # event one datetime & location
        frm_event_one = Gtk.Frame()
        frm_event_one.add_css_class("frame-sidepane")
        frm_event_one.set_label("event one")
        frm_label_one = frm_event_one.get_label_widget()
        frm_label_one.add_css_class("frame-label")

        lbl_datetime_one = Gtk.Label(label="date & time")
        lbl_datetime_one.add_css_class("label")
        # lbl_datetime.set_halign(Gtk.Align.START)
        lbl_datetime_one.set_xalign(0.1)
        ent_datetime_one = Gtk.Entry()
        # ent_datetime.set_hexpand(True)
        ent_datetime_one.set_placeholder_text("yyyy MM dd hh mm (ss)")
        ent_datetime_one.set_tooltip_text(
            """ year month day hour minute (second)
second is optional """
        )
        lbl_location_one = Gtk.Label(lable="location")
        lbl_location_one

        box_datetime_one = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_datetime_one.set_visible(True)
        box_datetime_one.append(lbl_datetime_one)
        box_datetime_one.append(ent_datetime_one)
        frm_event_one.set_child(box_datetime_one)
        # event two datetime & location

        box_side_pane_widgets.append(frm_event_one)
        # box_side_pane_widgets.append(frm_event_two)

        box_side_pane_main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box_side_pane_main.set_visible(True)
        box_side_pane_main.append(box_side_pane_buttons)
        box_side_pane_main.append(box_side_pane_widgets)

        return box_side_pane_main

    def create_pane_icon(self, icon_name):
        return Gtk.Image.new_from_file(f"{self.icons_folder}{icon_name}")

    # Button handlers
    def obc_default(self, widget, data):
        print(f"{data} clicked : obc_default()")

    def obc_settings(self, widget, data):
        print(f"{data} clicked")

    def obc_event_one(self, widget, data):
        print(f"{data} clicked")
        # if not hasattr(self, "wgt_event_one"):
        #     print("obc_event_one : no 'wgt_event_one' : creating ...")
        #     # create widget for event one data input
        #     from ui.widgets.event_widget import EventWidget  # type: ignore

        #     self.wgt_event_one = EventWidget("event one")
        #     self.box_side_pane_widgets.append(self.wgt_event_one)
        #     self.wgt_event_one.set_visible(True)
        #     self.box_side_pane_widgets.set_visible(True)

    def obc_event_two(self, widget, data):
        print(f"{data} clicked")

    def obc_file_save(self, widget, data):
        print(f"{data} clicked")

    def obc_file_load(self, widget, data):
        print(f"{data} clicked")
